import json
import logging
from typing import Any, Dict, List, Optional
import pathlib

# Thiết lập logging cơ bản
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AutomationBridge")

class AutomationBridge:
    def __init__(self, config_path: str = None):
        """
        Khởi tạo AutomationBridge, đọc cấu hình từ file.
        """
        self.project_root = pathlib.Path(__file__).parent.parent.absolute()
        
        if config_path is None:
            config_path = str(self.project_root / "config.json")
            
        self.config = self._load_config(config_path)
        logger.info("AutomationBridge initialized.")
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Đọc file cấu hình. Tạm thời trả về dict rỗng nếu chưa có file.
        """
        path = pathlib.Path(config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        logger.warning(f"Config file {config_path} not found. Using default empty config.")
        return {}

    def _get_absolute_path(self, path_str: str) -> str:
        """Helper chuyển đổi đường dẫn tương đối thành tuyệt đối dựa vào project root"""
        import os
        if os.path.isabs(path_str):
            return path_str
        return str(self.project_root / path_str)

    # ==========================================
    # 9 ACTION CONTRACTS (SKELETONS)
    # ==========================================

    def query_rag(self, query: str) -> Dict[str, Any]:
        """ Action 1: Truy xuất tài liệu mềm qua Qdrant Vector DB """
        import urllib.request
        import urllib.error
        import json
        logger.info(f"Executing query_rag with query: {query}")
        
        # 1. Lấy embedding của query (lam giau bang ontology + core KB)
        enriched = self._ontology_enrich(query)
        enriched_kb = self._corekb_enrich(query)
        embed_input = " ".join([p for p in (query, enriched, enriched_kb) if p]).strip()
        if enriched or enriched_kb:
            logger.info(f"Enrich: ontology={enriched[:80]} | kb={enriched_kb[:80]}")
        ollama_base = self.config.get("ollama_base_url", "http://127.0.0.1:11434")
        ollama_url = f"{ollama_base.rstrip('/')}/api/embed"
        embed_payload = {
            "model": "bge-m3",
            "input": [embed_input]
        }
        
        try:
            req_embed = urllib.request.Request(
                ollama_url, 
                data=json.dumps(embed_payload).encode('utf-8'), 
                headers={"Content-Type": "application/json"}, 
                method="POST"
            )
            with urllib.request.urlopen(req_embed) as response:
                result = json.loads(response.read().decode('utf-8'))
                query_vector = result.get("embeddings", [])[0]
        except Exception as e:
            logger.error(f"Failed to get query embedding from Ollama: {str(e)}")
            return {
                "ok": False,
                "error": {
                    "code": "EMBEDDING_ERROR",
                    "message": f"Lỗi lấy vector embedding từ Ollama: {str(e)}"
                }
            }
            
        # 2. Truy vấn Qdrant để tìm top-5 kết quả tương đồng nhất
        qdrant_base = self.config.get("qdrant_base_url", "http://127.0.0.1:6333")
        qdrant_url = f"{qdrant_base.rstrip('/')}/collections/physics_kb/points/search"
        search_payload = {
            "vector": query_vector,
            "limit": 3,
            "with_payload": True
        }
        
        try:
            req_search = urllib.request.Request(
                qdrant_url, 
                data=json.dumps(search_payload).encode('utf-8'), 
                headers={"Content-Type": "application/json"}, 
                method="POST"
            )
            with urllib.request.urlopen(req_search) as response:
                result = json.loads(response.read().decode('utf-8'))
                search_results = result.get("result", [])
                
            # 3. Trích xuất văn bản và nguồn (lọc theo ngưỡng độ liên quan)
            min_score = float(self.config.get("rag_min_score", 0.42))
            context_pieces = []
            sources = []
            
            for item in search_results:
                payload = item.get("payload", {})
                score = item.get("score", 0.0)
                if score < min_score:
                    continue  # bỏ qua kết quả không liên quan
                text = payload.get("text", "")
                
                source_file = payload.get("source_file", "unknown")
                page = payload.get("page", "?")
                
                # Format đoạn văn nối tiếp nhau có đánh dấu ranh giới
                context_pieces.append(f"--- NGUỒN: {source_file} (Trang {page}) [Độ tin cậy: {score:.4f}] ---\n{text}")
                
                sources.append({
                    "file": source_file,
                    "page": page,
                    "score": score
                })
                
            if not context_pieces:
                return {
                    "ok": True,
                    "data": {
                        "context": "KHÔNG tìm thấy tài liệu liên quan trong kho kiến thức (mọi kết quả đều dưới ngưỡng độ liên quan).",
                        "sources": [],
                        "relevant": False
                    }
                }
            
            context = "\n\n".join(context_pieces)
            
            return {
                "ok": True,
                "data": {
                    "context": context,
                    "sources": sources,
                    "relevant": True
                }
            }
        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}")
            return {
                "ok": False,
                "error": {
                    "code": "QDRANT_SEARCH_ERROR",
                    "message": f"Không thể truy xuất Qdrant: {str(e)}"
                }
            }

    def query_kg(self, query: str) -> Dict[str, Any]:
        """ Action 2: Truy vấn Core KB (mạng lưới sự kiện) — tìm fact + crawl láng giềng bậc 1 """
        import sqlite3
        import json as _json
        logger.info(f"Executing query_kg with query: {query}")
        kb_path = self._get_absolute_path(self.config.get("kb_path", "core_kb.db"))
        try:
            conn = sqlite3.connect(kb_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            keywords = [k for k in query.split() if len(k) >= 2]
            if not keywords:
                return {"ok": True, "data": {"context": "", "results": []}}

            # tim facts khớp (AND trước, OR sau)
            conds = " AND ".join(["(name LIKE ? OR label LIKE ? OR description LIKE ?)" for _ in keywords])
            params = []
            for kw in keywords:
                params.extend([f"%{kw}%", f"%{kw}%", f"%{kw}%"])
            cur.execute(f"SELECT id, type, name, label, description, value_json, unit, source FROM facts WHERE {conds} LIMIT 8", params)
            matched = cur.fetchall()
            if not matched:
                conds = " OR ".join(["(name LIKE ? OR label LIKE ? OR description LIKE ?)" for _ in keywords])
                cur.execute(f"SELECT id, type, name, label, description, value_json, unit, source FROM facts WHERE {conds} LIMIT 8", params)
                matched = cur.fetchall()
            if not matched:
                return {"ok": True, "data": {"context": "Không tìm thấy mục khớp trong Core KB.", "results": []}}

            lines = []
            results = []
            seen = set()
            for m in matched:
                fid = m["id"]
                if fid in seen:
                    continue
                seen.add(fid)
                val = ""
                if m["value_json"]:
                    try:
                        v = _json.loads(m["value_json"])
                        if isinstance(v, dict):
                            if v.get("latex"):
                                val = f" : {v['latex']}"
                            elif v.get("value") is not None:
                                val = f" = {v['value']}"
                                if v.get("unit"):
                                    val += f" {v['unit']}"
                        else:
                            val = f" = {v}"
                    except Exception:
                        val = ""
                unit = f" [{m['unit']}]" if m["unit"] else ""
                src = f" (nguồn: {m['source']})" if m["source"] else ""
                lines.append(f"• [{m['type']}] {m['label']}{val}{unit}{src}")
                if m["description"]:
                    lines.append(f"   {m['description']}")
                results.append({
                    "id": fid, "type": m["type"], "name": m["name"], "label": m["label"],
                    "description": m["description"], "value": val.strip(),
                    "unit": m["unit"], "source": m["source"]
                })
                # crawl láng giềng bậc 1 (outgoing + incoming)
                cur.execute("""SELECT e.relation, f.label FROM fact_edges e
                               JOIN facts f ON f.id=e.target_id
                               WHERE e.source_id=? ORDER BY e.weight DESC""", (fid,))
                for rel, tlabel in cur.fetchall():
                    lines.append(f"   └ {rel} → {tlabel}")
                cur.execute("""SELECT e.relation, f.label FROM fact_edges e
                               JOIN facts f ON f.id=e.source_id
                               WHERE e.target_id=?""", (fid,))
                for rel, slabel in cur.fetchall():
                    lines.append(f"   └ ← {slabel} ({rel})")
            conn.close()
            return {"ok": True, "data": {"context": "\n".join(lines), "results": results}}
        except Exception as e:
            logger.error(f"query_kg failed: {e}")
            return {"ok": False, "error": {"code": "DB_ERROR", "message": str(e)}}


    def _ontology_enrich(self, query: str) -> str:
        """Crawl ontology lay cac khai niem lien quan, tra ve chuoi ten (cho hybrid retrieval)."""
        import sqlite3
        ontology_path = self._get_absolute_path(self.config.get("ontology_path", "ontology.db"))
        try:
            conn = sqlite3.connect(ontology_path)
            cur = conn.cursor()
            keywords = [k for k in query.split() if len(k) >= 2]
            if not keywords:
                return ""
            conds = " OR ".join(["name LIKE ?" for _ in keywords])
            params = [f"%{kw}%" for kw in keywords]
            cur.execute(f"SELECT id, name FROM nodes WHERE {conds} LIMIT 4", params)
            matched = cur.fetchall()
            if not matched:
                return ""
            concepts = []
            for mid, mname in matched:
                concepts.append(mname)
                cur.execute("""SELECT n.name FROM edges e JOIN nodes n ON n.id=e.target_id
                               WHERE e.source_id=? AND e.relation != 'is_a'""", (mid,))
                concepts.extend(r[0] for r in cur.fetchall())
                cur.execute("""SELECT n.name FROM edges e JOIN nodes n ON n.id=e.source_id
                               WHERE e.target_id=? AND e.relation != 'is_a'""", (mid,))
                concepts.extend(r[0] for r in cur.fetchall())
            conn.close()
            seen = set()
            out = []
            for c in concepts:
                if c not in seen:
                    seen.add(c)
                    out.append(c)
            return " ".join(out)
        except Exception as e:
            logger.warning(f"ontology enrich failed: {e}")
            return ""

    def _corekb_enrich(self, query: str) -> str:
        """Crawl Core KB lay cac fact lien quan, tra ve chuoi label (cho hybrid retrieval)."""
        import sqlite3
        kb_path = self._get_absolute_path(self.config.get("kb_path", "core_kb.db"))
        try:
            conn = sqlite3.connect(kb_path)
            cur = conn.cursor()
            keywords = [k for k in query.split() if len(k) >= 2]
            if not keywords:
                return ""
            conds = " OR ".join(["(name LIKE ? OR label LIKE ?)" for _ in keywords])
            params = []
            for kw in keywords:
                params.extend([f"%{kw}%", f"%{kw}%"])
            cur.execute(f"SELECT id, label FROM facts WHERE {conds} LIMIT 4", params)
            matched = cur.fetchall()
            if not matched:
                return ""
            terms = []
            for fid, label in matched:
                terms.append(label)
                cur.execute("SELECT f.label FROM fact_edges e JOIN facts f ON f.id=e.target_id WHERE e.source_id=? LIMIT 6", (fid,))
                terms.extend(r[0] for r in cur.fetchall())
                cur.execute("SELECT f.label FROM fact_edges e JOIN facts f ON f.id=e.source_id WHERE e.target_id=? LIMIT 6", (fid,))
                terms.extend(r[0] for r in cur.fetchall())
            conn.close()
            seen = set()
            out = []
            for t in terms:
                if t and t not in seen:
                    seen.add(t)
                    out.append(t)
            return " ".join(out)
        except Exception as e:
            logger.warning(f"corekb enrich failed: {e}")
            return ""

    def query_ontology(self, query: str) -> Dict[str, Any]:
        """ Action: Truy vấn đồ thị tri thức (ontology graph) — tìm khái niệm + crawl láng giềng bậc 1"""
        import sqlite3
        logger.info(f"Executing query_ontology with query: {query}")
        ontology_path = self._get_absolute_path(self.config.get("ontology_path", "ontology.db"))
        try:
            conn = sqlite3.connect(ontology_path)
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            keywords = [k for k in query.split() if len(k) >= 2]
            if not keywords:
                return {"ok": True, "data": {"context": "", "nodes": []}}

            # 1. Tim node khop theo ten (dung AND de chinh xac hon)
            conds = " AND ".join(["name LIKE ?" for _ in keywords])
            params = [f"%{kw}%" for kw in keywords]
            cur.execute(f"SELECT id, name, tier, category FROM nodes WHERE {conds} LIMIT 8", params)
            matched = cur.fetchall()

            if not matched:
                # thu OR (nen hon)
                conds = " OR ".join(["name LIKE ?" for _ in keywords])
                cur.execute(f"SELECT id, name, tier, category FROM nodes WHERE {conds} LIMIT 8", params)
                matched = cur.fetchall()
            if not matched:
                return {"ok": True, "data": {"context": "Không tìm thấy khái niệm khớp trong đồ thị tri thức.", "nodes": []}}

            lines = []
            seen_nodes = set()
            for m in matched:
                mid = m["id"]
                mname = m["name"]
                # is_a -> parent (branch/trunk)
                cur.execute("""SELECT n.name FROM edges e JOIN nodes n ON n.id=e.target_id
                               WHERE e.source_id=? AND e.relation='is_a'""", (mid,))
                parents = [r["name"] for r in cur.fetchall()]
                # neighbors (cross-links, relation != is_a)
                cur.execute("""SELECT e.relation, n.name, n.tier, n.category
                               FROM edges e JOIN nodes n ON n.id=e.target_id
                               WHERE e.source_id=? AND e.relation != 'is_a'""", (mid,))
                neighbors = cur.fetchall()
                # reverse edges (who points to this node)
                cur.execute("""SELECT e.relation, n.name FROM edges e JOIN nodes n ON n.id=e.source_id
                               WHERE e.target_id=? AND e.relation != 'is_a'""", (mid,))
                incoming = cur.fetchall()

                parent_str = ", ".join(parents) if parents else "—"
                lines.append(f"• {mname} [tầng {m['tier']}{', ' + m['category'] if m['category'] else ''}] — thuộc: {parent_str}")
                for r in neighbors:
                    lines.append(f"   └ {r['relation']} → {r['name']}")
                for r in incoming:
                    lines.append(f"   └ ← {r['name']} ({r['relation']})")
                seen_nodes.add(mname)

            # crawl cầu nối nhận thức -> facts (core KB, TẠM THỜI)
            kb_path = self._get_absolute_path(self.config.get("kb_path", "core_kb.db"))
            try:
                kb_conn = sqlite3.connect(kb_path)
                kb_conn.row_factory = sqlite3.Row
                kb_cur = kb_conn.cursor()
                for m in matched:
                    kb_cur.execute("""SELECT cl.relation, cl.confidence, cl.status, f.label, f.value_json, f.type
                                      FROM cross_links cl JOIN facts f ON f.name = cl.fact_name
                                      WHERE cl.ontology_node = ? ORDER BY cl.confidence DESC""", (m["name"],))
                    for clr in kb_cur.fetchall():
                        flag = " [TẠM THỜI]" if clr["status"] != "verified" else " [đã xác minh]"
                        val = ""
                        if clr["value_json"]:
                            import json as _cljson
                            try:
                                _cv = _cljson.loads(clr["value_json"])
                                if isinstance(_cv, dict):
                                    if _cv.get("latex"):
                                        val = f" : {_cv['latex']}"
                                    elif _cv.get("value") is not None:
                                        val = f" = {_cv['value']}"
                            except Exception:
                                pass
                        lines.append(f"   ✦ {clr['relation']} → [{clr['type']}] {clr['label']}{val}{flag} (conf {clr['confidence']})")
                kb_conn.close()
            except Exception as e:
                logger.warning(f"crosslink crawl failed: {e}")

            context = "\n".join(lines)
            return {"ok": True, "data": {"context": context, "nodes": list(seen_nodes)}}
        except Exception as e:
            logger.error(f"query_ontology failed: {e}")
            return {"ok": False, "error": {"code": "ONTOLOGY_ERROR", "message": str(e)}}

    def calculate(self, expression: str, variables: Dict[str, float]) -> Dict[str, Any]:
        """ Action 3: Tính toán biểu thức toán học bằng SymPy """
        import sympy
        logger.info(f"Executing calculate for expression: {expression} with vars: {variables}")
        try:
            expr = sympy.sympify(expression)
            subs_dict = {sympy.Symbol(k): v for k, v in variables.items()}
            result = expr.evalf(subs=subs_dict)
            
            if result.is_real:
                val = float(result)
            else:
                val = str(result)
                
            return {"ok": True, "data": {"result": val, "unit": ""}}
        except Exception as e:
            logger.error(f"calculate failed: {str(e)}")
            return {"ok": False, "error": {"code": "CALC_ERROR", "message": f"Lỗi tính toán: {str(e)}"}}

    def run_simulation(self, executable: str, args: List[str], input_file: str, working_dir: str, timeout_sec: int) -> Dict[str, Any]:
        """ 
        Action 4: Thực thi code mô phỏng vật lý trong Sandbox.
        Lưu ý: input_file (nếu có) sẽ được truyền làm tham số vị trí cuối cùng của câu lệnh.
        """
        import tempfile
        import subprocess
        import os
        import shutil
        from datetime import datetime

        logger.info(f"Executing run_simulation for {executable}")
        try:
            # 1. Tạo thư mục Sandbox cô lập
            base_sandbox_dir = self._get_absolute_path(self.config.get("sandbox_base_dir", "sandbox_runs"))
            os.makedirs(base_sandbox_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sandbox_dir = tempfile.mkdtemp(prefix=f"run_{timestamp}_", dir=base_sandbox_dir)
            
            # 2. Chuẩn bị file log và input
            stdout_log_path = os.path.join(sandbox_dir, "stdout.log")
            stderr_log_path = os.path.join(sandbox_dir, "stderr.log")
            cmd_log_path = os.path.join(sandbox_dir, "command.log")
            
            # Copy input file vào sandbox nếu có
            sandbox_input_file = ""
            if input_file and os.path.exists(input_file):
                sandbox_input_file = os.path.join(sandbox_dir, os.path.basename(input_file))
                shutil.copy2(input_file, sandbox_input_file)
            
            # Dựng command array
            cmd = [executable] + args
            if sandbox_input_file:
                cmd.append(sandbox_input_file)
                
            # Ghi lại command đã chạy để dễ debug
            with open(cmd_log_path, 'w', encoding='utf-8') as f:
                f.write(f"Command: {' '.join(cmd)}\n")
                f.write(f"Timeout: {timeout_sec}s\n")
                f.write(f"Sandbox Dir: {sandbox_dir}\n")
                
            # 3. Thực thi Subprocess với cây tiến trình đầy đủ (Process Group) để diệt sạch khi Timeout
            with open(stdout_log_path, 'w', encoding='utf-8') as f_out, open(stderr_log_path, 'w', encoding='utf-8') as f_err:
                process = subprocess.Popen(
                    cmd,
                    cwd=sandbox_dir,
                    stdout=f_out,
                    stderr=f_err,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                )
                
                try:
                    process.wait(timeout=timeout_sec)
                except subprocess.TimeoutExpired:
                    # Giết toàn bộ cây tiến trình bằng taskkill trên Windows
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], capture_output=True)
                    process.wait()
                    logger.error(f"Simulation timed out after {timeout_sec} seconds")
                    return {
                        "ok": False,
                        "error": {
                            "code": "TIMEOUT",
                            "message": f"Quá trình mô phỏng bị hủy do vượt quá giới hạn thời gian {timeout_sec} giây."
                        }
                    }
                
            return {
                "ok": True, 
                "data": {
                    "sandbox_dir": sandbox_dir, 
                    "stdout_log_path": stdout_log_path, 
                    "stderr_log_path": stderr_log_path, 
                    "exit_code": process.returncode
                }
            }
            
        except Exception as e:
            logger.error(f"Simulation failed: {str(e)}")
            return {
                "ok": False,
                "error": {
                    "code": "EXECUTION_FAILED",
                    "message": f"Lỗi khi thực thi mô phỏng: {str(e)}"
                }
            }

    def read_output(self, file_path: str, format: str, extract_keys: List[str]) -> Dict[str, Any]:
        """ Action 5: Đọc số liệu từ file kết quả (CSV/TXT) """
        import csv
        import re
        import os

        logger.info(f"Executing read_output on {file_path}")
        
        # Cho phép LLM đưa đường dẫn tương đối so với project root (hoặc nếu là absolute thì giữ nguyên)
        abs_file_path = file_path if os.path.isabs(file_path) else self._get_absolute_path(file_path)
        
        if not os.path.exists(abs_file_path):
            return {
                "ok": False,
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": f"Không tìm thấy file: {abs_file_path}"
                }
            }

        try:
            extracted = {}
            with open(abs_file_path, 'r', encoding='utf-8') as f:
                if format.lower() == 'csv':
                    # Đọc CSV giả định dạng row chứa "key, value" hoặc mảng song song
                    reader = csv.reader(f)
                    rows = list(reader)
                    for row in rows:
                        for i, cell in enumerate(row):
                            cell_clean = cell.strip()
                            if cell_clean in extract_keys:
                                if i + 1 < len(row):
                                    try:
                                        extracted[cell_clean] = float(row[i+1].strip())
                                    except ValueError:
                                        extracted[cell_clean] = row[i+1].strip()
                else: 
                    # Định dạng txt
                    content = f.read()
                    for key in extract_keys:
                        # Tìm regex dạng: key = value hoặc key : value
                        pattern = re.compile(rf"{re.escape(key)}\s*[:=]\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)")
                        match = pattern.search(content)
                        if match:
                            extracted[key] = float(match.group(1))

            # Log warning nếu có key không tìm thấy (áp dụng cho cả CSV và TXT)
            missing_keys = set(extract_keys) - set(extracted.keys())
            if missing_keys:
                logger.warning(f"read_output: Không tìm thấy các keys sau trong {file_path}: {missing_keys}")

            return {
                "ok": True,
                "data": {
                    "extracted_values": extracted
                }
            }
        except Exception as e:
            logger.error(f"Failed to read output: {str(e)}")
            return {
                "ok": False,
                "error": {
                    "code": "READ_ERROR",
                    "message": f"Lỗi khi đọc file output: {str(e)}"
                }
            }

    def compare_experiment(self, simulation_data: Dict[str, float], experiment_data: Dict[str, float]) -> Dict[str, Any]:
        """ 
        Action 6: Đối chiếu kết quả mô phỏng và thực nghiệm.
        Lưu ý: Ngưỡng 5% dùng ở đây chỉ để tạo Cảnh Báo kết luận cho User (khác với ngưỡng 1% khắt khe của verify_claims).
        """
        logger.info("Executing compare_experiment")
        deviations = {}
        passed_all = True
        conclusion_parts = []
        
        try:
            for key, exp_val in experiment_data.items():
                if key in simulation_data:
                    sim_val = simulation_data[key]
                    if exp_val == 0:
                        deviation = 0.0 if sim_val == 0 else float('inf')
                    else:
                        deviation = abs(sim_val - exp_val) / abs(exp_val) * 100.0
                    
                    deviations[key] = deviation
                    # Threshold logic cơ bản (có thể điều chỉnh sau)
                    if deviation > 5.0: 
                        passed_all = False
                        conclusion_parts.append(f"{key} lệch {deviation:.2f}% (sim={sim_val}, exp={exp_val})")
                else:
                    conclusion_parts.append(f"Thiếu dữ liệu mô phỏng cho {key}")
                    passed_all = False
                    
            if passed_all:
                conclusion = "Mô phỏng khớp tốt với thực nghiệm (sai số <= 5%)."
            else:
                conclusion = "Có sai lệch đáng kể: " + "; ".join(conclusion_parts)
                
            return {
                "ok": True,
                "data": {
                    "deviations": deviations,
                    "conclusion": conclusion
                }
            }
        except Exception as e:
            logger.error(f"Failed to compare experiment: {str(e)}")
            return {
                "ok": False,
                "error": {
                    "code": "COMPARE_ERROR",
                    "message": f"Lỗi khi tính toán so sánh: {str(e)}"
                }
            }

    def propose_parameter_change(self, parameters: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """ Action 7: Yêu cầu User phê duyệt việc đổi tham số (Human-in-the-loop) """
        import os
        import json
        logger.info("Executing propose_parameter_change")
        
        pending_file = self._get_absolute_path("pending_changes.json")
        
        # 1. Nếu file đã tồn tại, kiểm tra xem User đã duyệt hay chưa
        if os.path.exists(pending_file):
            try:
                with open(pending_file, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                
                # Đối chiếu xem có đúng là yêu cầu hiện tại đang được duyệt không
                if saved_data.get("parameters") == parameters:
                    status = saved_data.get("status", "pending_approval")
                    feedback = saved_data.get("feedback", "")
                    
                    if status in ["approved", "rejected"]:
                        # Đã có quyết định từ User -> xóa file và hoàn về kết quả
                        os.remove(pending_file)
                        return {
                            "ok": True,
                            "data": {
                                "status": status,
                                "feedback": feedback
                            }
                        }
                    else:
                        # Vẫn đang chờ
                        return {
                            "ok": True,
                            "data": {
                                "status": "pending_approval",
                                "feedback": f"Đang chờ User phản hồi trong file {pending_file}"
                            }
                        }
            except Exception as e:
                logger.error(f"Error reading {pending_file}: {e}")
                
        # 2. Tạo đề xuất mới (chưa có file, hoặc parameters mới)
        proposal = {
            "status": "pending_approval",
            "feedback": "",
            "parameters": parameters,
            "instruction": "Đổi 'status' thành 'approved' hoặc 'rejected', nhập 'feedback' và lưu file này lại."
        }
        
        try:
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(proposal, f, indent=4, ensure_ascii=False)
                
            return {
                "ok": True,
                "data": {
                    "status": "pending_approval",
                    "feedback": f"Đã xuất đề xuất tham số ra file {pending_file}. Vui lòng sửa file để duyệt."
                }
            }
        except Exception as e:
            logger.error(f"Failed to create pending changes file: {e}")
            return {
                "ok": False,
                "error": {
                    "code": "FILE_WRITE_ERROR",
                    "message": f"Không thể tạo file đề xuất: {str(e)}"
                }
            }

    def verify_claims(self, claims: List[Dict[str, Any]]) -> Dict[str, Any]:
        """ Action 8: Đối chiếu độ lệch số liệu với Core KB (Tolerance 1%) và Uncertainty """
        import sqlite3
        import os
        logger.info("Executing verify_claims")
        kb_path = self._get_absolute_path(self.config.get("kb_path", "core_kb.db"))
        
        if not os.path.exists(kb_path):
            return {"ok": False, "error": {"code": "KB_NOT_FOUND", "message": "File core_kb.db chưa được khởi tạo."}}
            
        passed = True
        conflicts = []
        try:
            conn = sqlite3.connect(kb_path)
            cursor = conn.cursor()
            for claim in claims:
                entity = claim.get("entity")
                property_ = claim.get("property")
                claim_val = claim.get("value")
                
                import json as _vjson
                cursor.execute(
                    "SELECT value_json FROM facts WHERE type='constant' AND (name = ? OR name LIKE ? OR label LIKE ?) LIMIT 1",
                    (f"{entity}_{property_}", f"%{entity}%", f"%{entity}%"))
                row = cursor.fetchone()

                if row:
                    _vd = _vjson.loads(row[0]) if row[0] else {}
                    kb_val = _vd.get("value") if isinstance(_vd, dict) else None
                    uncertainty = (_vd.get("uncertainty") or 0.0) if isinstance(_vd, dict) else 0.0
                    if kb_val is None:
                        continue
                    
                    if kb_val == 0:
                        diff_pct = 0.0 if claim_val == 0 else float('inf')
                    else:
                        diff_pct = abs(claim_val - kb_val) / abs(kb_val) * 100.0
                        
                    # Ưu tiên kiểm tra Uncertainty range
                    lower_bound = kb_val - uncertainty
                    upper_bound = kb_val + uncertainty
                    
                    claim_passed = False
                    if lower_bound <= claim_val <= upper_bound:
                        claim_passed = True
                    elif diff_pct <= 1.0:
                        claim_passed = True
                        
                    if not claim_passed:
                        passed = False
                        conflicts.append({
                            "claim": f"{entity}.{property_}={claim_val}",
                            "kb_value": kb_val,
                            "uncertainty": uncertainty,
                            "difference_pct": diff_pct
                        })
                else:
                    # Nếu claim không nằm trong Core KB, tạm thời coi như pass vì KB không cover hết,
                    # hoặc có thể tuỳ config mà trả về cảnh báo. Ở đây hệ thống ưu tiên không block nếu không có base truth.
                    pass
            conn.close()
            
            return {
                "ok": True, 
                "data": {
                    "passed": passed, 
                    "conflicts": conflicts
                }
            }
        except Exception as e:
            logger.error(f"verify_claims failed: {e}")
            return {"ok": False, "error": {"code": "VERIFY_ERROR", "message": str(e)}}

    @staticmethod
    def _restore_latex_backslash(s: str) -> str:
        """json.loads nuốt backslash trước f/b/t/r/n khi LLM trả LaTeX single-backslash."""
        if not s:
            return s
        import re
        BS = chr(92)
        s = (s.replace(chr(12), BS + 'f')
              .replace(chr(8), BS + 'b')
              .replace(chr(9), BS + 't')
              .replace(chr(13), BS + 'r'))
        # newline theo sau chữ thường = macro \n (nabla, nu, ni...) bị nuốt
        s = re.sub(chr(10) + r'(?=[a-z])', BS + 'n', s)
        return s

    def finish(self, final_answer: str) -> Dict[str, Any]:
        """ Action 9: Chấm dứt vòng lặp ReAct, sinh câu trả lời """
        logger.info("Executing finish")
        return {"ok": True, "data": {"status": "done"}}

    # ==========================================
    # REACT LOOP RUNNER (SKELETON)
    # ==========================================

    def run_react_loop(self, initial_prompt: str) -> str:
        """ Vòng lặp chính của ReAct Automation Bridge """
        import urllib.request
        import urllib.error
        import re
        
        logger.info(f"Starting ReAct loop with prompt: {initial_prompt}")
        
        ollama_base = self.config.get("ollama_base_url", "http://127.0.0.1:11434")
        chat_url = f"{ollama_base.rstrip('/')}/api/chat"
        model_name = self.config.get("model_name", "qwen3:8b")
        
        system_prompt = (
            "Bạn là AutomationBridge, Trợ lý AI vật lý hạt nhân 100% offline.\n"
            "Nhiệm vụ của bạn là giải quyết yêu cầu của người dùng bằng cách gọi tool. Mỗi lượt CHỈ gọi 1 tool.\n"
            "\n"
            "Các tools hiện có:\n"
            "1. query_rag(query: str) - Tra cứu kiến thức trong kho tài liệu (KHOA HỌC) - LUÔN gọi đầu tiên cho mọi câu hỏi kiến thức.\n"
            "2. query_kg(query: str) - Truy vấn Core KB (mạng lưới sự kiện: hằng số, định luật, công thức, đồng vị + các mục liên kết).\n"
            "3. query_ontology(query: str) - Truy vấn đồ thị tri thức (KHÁI NIỆM chắc chắn) + cầu nối tới Core KB (fact TẠM THỜI, chưa xác minh) — lấy khung + dữ liệu liên quan.\n"
            "4. calculate(expression: str, variables: dict) - Tính toán số học.\n"
            "5. run_simulation(...) - Chạy mô phỏng.\n"
            "6. read_output(...) - Đọc kết quả file.\n"
            "7. compare_experiment(...) - So sánh mô phỏng với thực nghiệm.\n"
            "8. propose_parameter_change(...) - Đề xuất thay đổi tham số.\n"
            "9. verify_claims(claims: list) - Kiểm chứng luận điểm.\n"
            "10. finish(final_answer: str) - Kết thúc và trả lời người dùng.\n"
            "\n"
            "QUY TẮC BẮT BUỘC (theo đúng thứ tự):\n"
            "1. Nếu câu hỏi cần kiến thức: gọi query_rag MỘT LẦN DUY NHẤT rồi DỪNG tra cứu.\n"
            "2. NGAY SAU KHI query_rag trả kết quả, PHẢI gọi finish với câu trả lời cho ĐÚNG câu hỏi ban đầu. TUYỆT ĐỐI KHÔNG gọi query_rag lần thứ hai, KHÔNG liệt kê thuật ngữ, KHÔNG khám phá chủ đề khác, KHÔNG hỏi ngược lại người dùng.\n"
            "3. Nếu kết quả query_rag ĐÚNG chủ đề câu hỏi: lấy nội dung đó làm căn cứ trả lời.\n"
            "4. Nếu kết quả query_rag KHÔNG liên quan: BỎ QUA nó và trả lời TRỰC TIẾP bằng kiến thức vật lý của bạn (công thức, định nghĩa, định luật chuẩn). Cuối câu ghi chú ngắn: '(KB không có tài liệu chi tiết về chủ đề này)'.\n"
            "5. Định nghĩa rõ mọi ký hiệu trước khi dùng. KHÔNG bịa công thức hay bước suy luận giả. Nếu không chắc, nói rõ 'không chắc chắn'.\n"
            "6. Viết công thức bằng LaTeX: $...$ cho inline, $$...$$ cho công thức nổi bật.\n"
            "7. KÝ HIỆU LaTeX CHUẨN (bắt buộc, tuyệt đối không viết sai): hằng số Planck rút gọn luôn là \\hbar (KHÔNG viết 'đ', 'ħ', 'h/2π' hay ký tự lạ). Độ bất định/Delta viết \\Delta (KHÔNG \\triangle). Bất đẳng thức dùng \\ge hoặc \\geq (KHÔNG dùng \\to). Giao hoán tử [x,p]=i\\hbar.\n"
            "\n"
            "8. HAI NÃO - PHÂN BIỆT ĐỘ TIN CẬY: Ontology (não trong) = KHÁI NIỆM ĐÃ DUYỆT → tin tuyệt đối, dùng làm khung lập luận. Core KB (não ngoài) = FACT TẠM THỜI (chưa xác minh) → chỉ dùng khi KHỚP ontology + kiến thức vật lý chuẩn. Nếu fact mâu thuẫn khái niệm ontology → ƯU TIÊN ontology + CHÈN nhãn '[CẢNH BÁO MÂU THUẪN]' đầu câu trả lời, nêu rõ khác biệt tiên đề vs dữ liệu, rồi hỏi ý kiến người dùng.\n"
            "\n"
            "ĐỊNH DẠNG OUTPUT: CHỈ trả về MỘT OBJECT JSON duy nhất:\n"
            '{"action": "tên_tool", "args": {"tham_so": "gia_tri"}}\n'
            "KHÔNG bọc trong Markdown ```json. KHÔNG có văn bản nào ngoài JSON. Kết thúc thì gọi finish với final_answer là câu trả lời đầy đủ cho người dùng."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": initial_prompt}
        ]
        
        max_steps = 5
        step = 0
        
        while step < max_steps:
            step += 1
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False,
                "format": "json" # Ép output ra format chuẩn json đối với Qwen3
            }
            
            try:
                req = urllib.request.Request(
                    chat_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={"Content-Type": "application/json"},
                    method="POST"
                )
                with urllib.request.urlopen(req) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    ai_reply = res_data.get("message", {}).get("content", "").strip()
            except Exception as e:
                logger.error(f"Failed to communicate with Ollama: {e}")
                return "Error: Cannot connect to Ollama API."
                
            logger.info(f"Step {step}: AI returned -> {ai_reply}")
            messages.append({"role": "assistant", "content": ai_reply})
            
            # Cố gắng parse JSON, đối phó với trường hợp model chèn mã markdown
            clean_reply = ai_reply
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', clean_reply, re.DOTALL)
            if match:
                clean_reply = match.group(1)
            
            try:
                action_data = json.loads(clean_reply)
                action_name = action_data.get("action")
                args = action_data.get("args", {})
                
                if not action_name:
                    raise ValueError("JSON missing 'action' field.")
                    
                if action_name == "finish":
                    final_ans = args.get("final_answer", "")
                    final_ans = self._restore_latex_backslash(final_ans)
                    self.finish(final_ans)
                    return final_ans
                    
                # Mapping tool
                tool_func = getattr(self, action_name, None)
                if not callable(tool_func) or action_name.startswith("_") or action_name == "run_react_loop":
                    raise ValueError(f"Unknown tool or forbidden action: {action_name}")
                    
                # Thực thi tool
                logger.info(f"Executing action: {action_name} with args: {args}")
                tool_result = tool_func(**args)
                
                # Trả kết quả tool cho AI
                tool_msg = f"Tool '{action_name}' returned: {json.dumps(tool_result, ensure_ascii=False)}"
                messages.append({"role": "user", "content": tool_msg})
                
            except Exception as e:
                err_msg = f"Lỗi parse JSON hoặc thực thi tool. Vui lòng đảm bảo bạn CHỈ TRẢ VỀ JSON HỢP LỆ. Lỗi chi tiết: {str(e)}"
                logger.warning(err_msg)
                messages.append({"role": "user", "content": err_msg})
                
        logger.error("Exceeded max steps in ReAct loop.")
        return "Error: Exceeded max steps in ReAct loop."

if __name__ == "__main__":
    # Test khởi tạo
    bridge = AutomationBridge()
    logger.info("Bridge skeleton ready.")
