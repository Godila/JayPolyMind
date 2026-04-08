"""
Graph-related API Routes
Uses project context mechanism with server-side state persistence
"""

import os
import traceback
import threading
from flask import request, jsonify, current_app

from . import graph_bp
from ..config import Config
from ..services.ontology_generator import OntologyGenerator
from ..services.graph_builder import GraphBuilderService
from ..services.text_processor import TextProcessor
from ..utils.file_parser import FileParser
from ..utils.logger import get_logger
from ..models.task import TaskManager, TaskStatus
from ..models.project import ProjectManager, ProjectStatus

# Get logger
logger = get_logger('jaypolymind.api')


def _get_storage():
    """Get Neo4jStorage from Flask app extensions."""
    storage = current_app.extensions.get('neo4j_storage')
    if not storage:
        raise ValueError("GraphStorage not initialized — check Neo4j connection")
    return storage


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    ext = os.path.splitext(filename)[1].lower().lstrip('.')
    return ext in Config.ALLOWED_EXTENSIONS


# ============== Project Management Interface ==============

@graph_bp.route('/project/<project_id>', methods=['GET'])
def get_project(project_id: str):
    """
    Get project details
    """
    project = ProjectManager.get_project(project_id)
    
    if not project:
        return jsonify({
            "success": False,
            "error": f"Project does not exist: {project_id}"
        }), 404
    
    return jsonify({
        "success": True,
        "data": project.to_dict()
    })


@graph_bp.route('/project/list', methods=['GET'])
def list_projects():
    """
    List all projects
    """
    limit = request.args.get('limit', 50, type=int)
    projects = ProjectManager.list_projects(limit=limit)
    
    return jsonify({
        "success": True,
        "data": [p.to_dict() for p in projects],
        "count": len(projects)
    })


@graph_bp.route('/project/<project_id>', methods=['DELETE'])
def delete_project(project_id: str):
    """
    Delete project
    """
    success = ProjectManager.delete_project(project_id)

    if not success:
        return jsonify({
            "success": False,
            "error": f"Project does not exist or deletion failed: {project_id}"
        }), 404

    return jsonify({
        "success": True,
        "message": f"Project deleted: {project_id}"
    })


@graph_bp.route('/project/<project_id>/reset', methods=['POST'])
def reset_project(project_id: str):
    """
    Reset project status (for rebuilding graph)
    """
    project = ProjectManager.get_project(project_id)

    if not project:
        return jsonify({
            "success": False,
            "error": f"Project does not exist: {project_id}"
        }), 404

    # Reset to ontology generated state
    if project.ontology:
        project.status = ProjectStatus.ONTOLOGY_GENERATED
    else:
        project.status = ProjectStatus.CREATED

    project.graph_id = None
    project.graph_build_task_id = None
    project.error = None
    ProjectManager.save_project(project)

    return jsonify({
        "success": True,
        "message": f"Project reset: {project_id}",
        "data": project.to_dict()
    })


# ============== Interface 1: Upload Files and Generate Ontology ==============

@graph_bp.route('/ontology/generate', methods=['POST'])
def generate_ontology():
    """
    Interface 1: Upload files and analyze to generate ontology definition

    Request method: multipart/form-data

    Parameters:
        files: Uploaded files (PDF/MD/TXT), multiple allowed
        simulation_requirement: Simulation requirement description (required)
        project_name: Project name (optional)
        additional_context: Additional notes (optional)

    Response:
        {
            "success": true,
            "data": {
                "project_id": "proj_xxxx",
                "ontology": {
                    "entity_types": [...],
                    "edge_types": [...],
                    "analysis_summary": "..."
                },
                "files": [...],
                "total_text_length": 12345
            }
        }
    """
    try:
        logger.info("=== Starting ontology generation ===")

        # Get parameters
        simulation_requirement = request.form.get('simulation_requirement', '')
        project_name = request.form.get('project_name', 'Unnamed Project')
        additional_context = request.form.get('additional_context', '')

        logger.debug(f"Project name: {project_name}")
        logger.debug(f"Simulation requirement: {simulation_requirement[:100]}...")

        if not simulation_requirement:
            return jsonify({
                "success": False,
                "error": "Please provide simulation requirement description (simulation_requirement)"
            }), 400

        # Get uploaded files
        uploaded_files = request.files.getlist('files')
        if not uploaded_files or all(not f.filename for f in uploaded_files):
            return jsonify({
                "success": False,
                "error": "Please upload at least one document file"
            }), 400

        # Create project
        project = ProjectManager.create_project(name=project_name)
        project.simulation_requirement = simulation_requirement
        logger.info(f"Project created: {project.project_id}")
        
        # Save files and extract text
        document_texts = []
        all_text = ""

        for file in uploaded_files:
            if file and file.filename and allowed_file(file.filename):
                # Save file to project directory
                file_info = ProjectManager.save_file_to_project(
                    project.project_id,
                    file,
                    file.filename
                )
                project.files.append({
                    "filename": file_info["original_filename"],
                    "size": file_info["size"]
                })

                # Extract text
                text = FileParser.extract_text(file_info["path"])
                text = TextProcessor.preprocess_text(text)
                document_texts.append(text)
                all_text += f"\n\n=== {file_info['original_filename']} ===\n{text}"

        if not document_texts:
            ProjectManager.delete_project(project.project_id)
            return jsonify({
                "success": False,
                "error": "No documents successfully processed. Please check file format"
            }), 400

        # Save extracted text
        project.total_text_length = len(all_text)
        ProjectManager.save_extracted_text(project.project_id, all_text)
        logger.info(f"Text extraction completed, total {len(all_text)} characters")

        # --- Deep Research (optional web grounding) ---
        enable_research = request.form.get('enable_research', '').lower()
        if enable_research == 'true':
            try:
                from ..services.deep_research import DeepResearchService
                logger.info("Deep Research v2 enabled, starting async research task...")
                researcher = DeepResearchService()

                task_manager = TaskManager()
                research_task_id = task_manager.create_task("Deep Research")
                project.research_task_id = research_task_id
                project.status = ProjectStatus.RESEARCHING
                ProjectManager.save_project(project)

                # Start background research thread
                thread = threading.Thread(
                    target=researcher.research_iterative,
                    args=(document_texts, simulation_requirement, research_task_id, task_manager),
                    daemon=True,
                )
                thread.start()

                # Return early -- frontend will poll task and then call /research/confirm
                return jsonify({
                    "success": True,
                    "data": {
                        "project_id": project.project_id,
                        "project_name": project.name,
                        "research_task_id": research_task_id,
                        "status": "researching",
                        "files": project.files,
                        "total_text_length": project.total_text_length,
                    }
                })
            except Exception as e:
                logger.warning(f"Deep Research failed to start, continuing without: {e}")

        # Generate ontology
        logger.info("Calling LLM to generate ontology definition...")
        generator = OntologyGenerator()
        ontology = generator.generate(
            document_texts=document_texts,
            simulation_requirement=simulation_requirement,
            additional_context=additional_context if additional_context else None
        )

        # Save ontology to project
        entity_count = len(ontology.get("entity_types", []))
        edge_count = len(ontology.get("edge_types", []))
        logger.info(f"Ontology generation completed: {entity_count} entity types, {edge_count} relation types")
        
        project.ontology = {
            "entity_types": ontology.get("entity_types", []),
            "edge_types": ontology.get("edge_types", [])
        }
        project.analysis_summary = ontology.get("analysis_summary", "")
        project.status = ProjectStatus.ONTOLOGY_GENERATED
        ProjectManager.save_project(project)
        logger.info(f"=== Ontology generation completed === Project ID: {project.project_id}")
        
        response_data = {
            "project_id": project.project_id,
            "project_name": project.name,
            "ontology": project.ontology,
            "analysis_summary": project.analysis_summary,
            "files": project.files,
            "total_text_length": project.total_text_length
        }
        if project.research_citations:
            response_data["research"] = {
                "citations": project.research_citations,
                "queries_used": project.research_queries,
            }

        return jsonify({
            "success": True,
            "data": response_data
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Interface 2: Build Graph ==============

@graph_bp.route('/build', methods=['POST'])
def build_graph():
    """
    Interface 2: Build graph based on project_id

    Request (JSON):
        {
            "project_id": "proj_xxxx",  // Required: from interface 1
            "graph_name": "Graph name",    // Optional
            "chunk_size": 500,          // Optional, default 500
            "chunk_overlap": 50         // Optional, default 50
        }

    Response:
        {
            "success": true,
            "data": {
                "project_id": "proj_xxxx",
                "task_id": "task_xxxx",
                "message": "Graph build task started"
            }
        }
    """
    try:
        logger.info("=== Starting graph build ===")

        # Parse request
        data = request.get_json() or {}
        project_id = data.get('project_id')
        logger.debug(f"Request parameters: project_id={project_id}")
        
        if not project_id:
            return jsonify({
                "success": False,
                "error": "Please provide project_id"
            }), 400

        # Get project
        project = ProjectManager.get_project(project_id)
        if not project:
            return jsonify({
                "success": False,
                "error": f"Project does not exist: {project_id}"
            }), 404

        # Check project status
        force = data.get('force', False)  # Force rebuild

        if project.status == ProjectStatus.CREATED:
            return jsonify({
                "success": False,
                "error": "Project has not generated ontology yet. Please call /ontology/generate first"
            }), 400

        if project.status == ProjectStatus.GRAPH_BUILDING and not force:
            return jsonify({
                "success": False,
                "error": "Graph is being built. Do not submit repeatedly. To force rebuild, add force: true",
                "task_id": project.graph_build_task_id
            }), 400

        # If force rebuild, reset status
        if force and project.status in [ProjectStatus.GRAPH_BUILDING, ProjectStatus.FAILED, ProjectStatus.GRAPH_COMPLETED]:
            project.status = ProjectStatus.ONTOLOGY_GENERATED
            project.graph_id = None
            project.graph_build_task_id = None
            project.error = None

        # Get configuration
        graph_name = data.get('graph_name', project.name or 'JayPolyMind Graph')
        chunk_size = data.get('chunk_size', project.chunk_size or Config.DEFAULT_CHUNK_SIZE)
        chunk_overlap = data.get('chunk_overlap', project.chunk_overlap or Config.DEFAULT_CHUNK_OVERLAP)

        # Update project configuration
        project.chunk_size = chunk_size
        project.chunk_overlap = chunk_overlap

        # Get extracted text
        text = ProjectManager.get_extracted_text(project_id)
        if not text:
            return jsonify({
                "success": False,
                "error": "Extracted text not found"
            }), 400

        # Get ontology
        ontology = project.ontology
        if not ontology:
            return jsonify({
                "success": False,
                "error": "Ontology definition not found"
            }), 400

        # Get storage in request context (background thread cannot access current_app)
        storage = _get_storage()

        # Create async task
        task_manager = TaskManager()
        task_id = task_manager.create_task(f"Build graph: {graph_name}")
        logger.info(f"Graph build task created: task_id={task_id}, project_id={project_id}")
        
        # Update project status
        project.status = ProjectStatus.GRAPH_BUILDING
        project.graph_build_task_id = task_id
        ProjectManager.save_project(project)

        # Start background task
        def build_task():
            build_logger = get_logger('jaypolymind.build')
            try:
                build_logger.info(f"[{task_id}] Starting graph build...")
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.PROCESSING,
                    message="Initializing graph build service..."
                )

                # Create graph builder service (storage passed from outer closure)
                builder = GraphBuilderService(storage=storage)

                # Chunk text
                task_manager.update_task(
                    task_id,
                    message="Chunking text...",
                    progress=5
                )
                chunks = TextProcessor.split_text(
                    text,
                    chunk_size=chunk_size,
                    overlap=chunk_overlap
                )
                total_chunks = len(chunks)

                # Create graph
                task_manager.update_task(
                    task_id,
                    message="Creating Zep graph...",
                    progress=10
                )
                graph_id = builder.create_graph(name=graph_name)

                # Update project graph_id
                project.graph_id = graph_id
                ProjectManager.save_project(project)

                # Set ontology
                task_manager.update_task(
                    task_id,
                    message="Setting ontology definition...",
                    progress=15
                )
                builder.set_ontology(graph_id, ontology)
                
                # Add text (progress_callback signature is (msg, progress_ratio))
                def add_progress_callback(msg, progress_ratio):
                    progress = 15 + int(progress_ratio * 40)  # 15% - 55%
                    task_manager.update_task(
                        task_id,
                        message=msg,
                        progress=progress
                    )

                task_manager.update_task(
                    task_id,
                    message=f"Starting to add {total_chunks} text chunks...",
                    progress=15
                )

                # Extract research facts for NER enrichment
                research_facts = None
                if project.research_confirmed and project.research_findings:
                    research_facts = [f.get('fact', '') for f in project.research_findings if f.get('enabled', True)]
                    if research_facts:
                        build_logger.info(f"[{task_id}] Injecting {len(research_facts)} research facts into NER")

                episode_uuids = builder.add_text_batches(
                    graph_id,
                    chunks,
                    batch_size=3,
                    progress_callback=add_progress_callback,
                    research_facts=research_facts,
                )

                # Neo4j processing is synchronous, no need to wait
                task_manager.update_task(
                    task_id,
                    message="Text processing completed...",
                    progress=85
                )

                # Create Citation nodes from research findings
                citation_count = 0
                if project.research_confirmed and project.research_findings:
                    task_manager.update_task(
                        task_id,
                        message="Creating citation nodes from research...",
                        progress=88
                    )
                    for finding in project.research_findings:
                        if not finding.get('enabled', True):
                            continue
                        try:
                            cit_uuid = storage.create_citation(graph_id, {
                                'fact': finding.get('fact', ''),
                                'source_url': finding.get('source_url', ''),
                                'source_title': finding.get('source_title', ''),
                                'confidence': finding.get('confidence', 'unverified'),
                                'research_round': finding.get('research_round', 0),
                            })
                            # Link to matching entities
                            linked = False
                            for entity_name in finding.get('related_entities', []):
                                entity = storage.find_entity_by_name(graph_id, entity_name)
                                if entity:
                                    storage.link_entity_to_citation(entity['uuid'], cit_uuid)
                                    build_logger.info(f"[{task_id}] Linked citation to entity '{entity['name']}'")
                                    linked = True
                                else:
                                    build_logger.debug(f"[{task_id}] Entity not found for linking: '{entity_name}'")

                            # Fallback: if no links made, try matching all graph entities against the fact text
                            if not linked:
                                fact_lower = finding.get('fact', '').lower()
                                all_nodes = storage.get_all_nodes(graph_id)
                                for node in all_nodes:
                                    node_name = node.get('name', '')
                                    if node_name and len(node_name) > 2 and node_name.lower() in fact_lower:
                                        storage.link_entity_to_citation(node['uuid'], cit_uuid)
                                        build_logger.info(f"[{task_id}] Fallback linked citation to entity '{node_name}'")
                                        linked = True
                            citation_count += 1
                        except Exception as ce:
                            build_logger.warning(f"[{task_id}] Failed to create citation: {ce}")
                    build_logger.info(f"[{task_id}] Created {citation_count} citation nodes")

                # Get graph data
                task_manager.update_task(
                    task_id,
                    message="Retrieving graph data...",
                    progress=95
                )
                graph_data = builder.get_graph_data(graph_id)

                # Update project status
                project.status = ProjectStatus.GRAPH_COMPLETED
                ProjectManager.save_project(project)

                node_count = graph_data.get("node_count", 0)
                edge_count = graph_data.get("edge_count", 0)
                build_logger.info(f"[{task_id}] Graph build completed: graph_id={graph_id}, nodes={node_count}, edges={edge_count}")

                # Complete
                task_manager.update_task(
                    task_id,
                    status=TaskStatus.COMPLETED,
                    message="Graph build completed",
                    progress=100,
                    result={
                        "project_id": project_id,
                        "graph_id": graph_id,
                        "node_count": node_count,
                        "edge_count": edge_count,
                        "chunk_count": total_chunks
                    }
                )

            except Exception as e:
                # Update project status to failed
                build_logger.error(f"[{task_id}] Graph build failed: {str(e)}")
                build_logger.debug(traceback.format_exc())

                project.status = ProjectStatus.FAILED
                project.error = str(e)
                ProjectManager.save_project(project)

                task_manager.update_task(
                    task_id,
                    status=TaskStatus.FAILED,
                    message=f"Build failed: {str(e)}",
                    error=traceback.format_exc()
                )

        # Start background thread
        thread = threading.Thread(target=build_task, daemon=True)
        thread.start()

        return jsonify({
            "success": True,
            "data": {
                "project_id": project_id,
                "task_id": task_id,
                "message": "Graph build task started. Query progress via /task/{task_id}"
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============== Task Query Interface ==============

@graph_bp.route('/task/<task_id>', methods=['GET'])
def get_task(task_id: str):
    """
    Query task status
    """
    task = TaskManager().get_task(task_id)

    if not task:
        return jsonify({
            "success": False,
            "error": f"Task does not exist: {task_id}"
        }), 404

    return jsonify({
        "success": True,
        "data": task.to_dict()
    })


@graph_bp.route('/tasks', methods=['GET'])
def list_tasks():
    """
    List all tasks
    """
    tasks = TaskManager().list_tasks()
    
    return jsonify({
        "success": True,
        "data": [t.to_dict() for t in tasks],
        "count": len(tasks)
    })


# ============== Deep Research Confirm ==============

@graph_bp.route('/research/confirm', methods=['POST'])
def confirm_research():
    """
    Confirm research findings and generate ontology.
    Called after user reviews findings in the review gate UI.

    Request (JSON):
        {
            "project_id": "proj_xxxx",
            "confirmed_finding_ids": ["uuid1", "uuid2", ...]
        }
    """
    try:
        data = request.get_json() or {}
        project_id = data.get('project_id')
        confirmed_ids = data.get('confirmed_finding_ids', [])

        if not project_id:
            return jsonify({"success": False, "error": "project_id required"}), 400

        project = ProjectManager.get_project(project_id)
        if not project:
            return jsonify({"success": False, "error": f"Project not found: {project_id}"}), 404

        # Get research results from task
        task_manager = TaskManager()
        task = task_manager.get_task(project.research_task_id) if project.research_task_id else None
        all_findings = []
        if task and task.result:
            all_findings = task.result.get("findings", [])

        # Filter to confirmed findings
        if confirmed_ids:
            confirmed = [f for f in all_findings if f.get("id") in confirmed_ids]
        else:
            # If no IDs provided, use all non-contradicted findings
            confirmed = [f for f in all_findings if f.get("confidence") != "contradicted"]

        # Build enriched_context from confirmed findings
        enriched_parts = []
        for f in confirmed:
            status_tag = f.get("confidence", "unverified").upper()
            enriched_parts.append(f"[{status_tag}] {f.get('fact', '')} (Source: {f.get('source_title', '')})")

        enriched_context = "\n".join(enriched_parts)
        additional_context = f"\n\n## Web Research Findings\n\n{enriched_context}" if enriched_context else None

        # Save findings to project
        project.research_findings = confirmed
        project.research_citations = [
            {"fact": f.get("fact", ""), "source_url": f.get("source_url", ""),
             "source_title": f.get("source_title", "")}
            for f in confirmed
        ]
        project.research_queries = task.result.get("queries_used", []) if task and task.result else []
        project.research_confirmed = True

        # Generate ontology with research context
        logger.info(f"Generating ontology with {len(confirmed)} confirmed research findings...")
        text = ProjectManager.get_extracted_text(project_id)
        document_texts = [text] if text else []

        generator = OntologyGenerator()
        ontology = generator.generate(
            document_texts=document_texts,
            simulation_requirement=project.simulation_requirement or "",
            additional_context=additional_context,
        )

        # Save ontology
        project.ontology = {
            "entity_types": ontology.get("entity_types", []),
            "edge_types": ontology.get("edge_types", []),
        }
        project.analysis_summary = ontology.get("analysis_summary", "")
        project.status = ProjectStatus.ONTOLOGY_GENERATED
        ProjectManager.save_project(project)

        entity_count = len(project.ontology.get("entity_types", []))
        edge_count = len(project.ontology.get("edge_types", []))
        logger.info(f"Ontology generated with research: {entity_count} entity types, {edge_count} edge types")

        response_data = project.to_dict()
        response_data["research"] = {
            "citations": project.research_citations,
            "queries_used": project.research_queries,
            "findings_count": len(confirmed),
        }

        return jsonify({"success": True, "data": response_data})

    except Exception as e:
        logger.error(f"Research confirm failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }), 500


@graph_bp.route('/research/skip', methods=['POST'])
def skip_research():
    """Skip research and generate ontology without web grounding."""
    try:
        data = request.get_json() or {}
        project_id = data.get('project_id')

        if not project_id:
            return jsonify({"success": False, "error": "project_id required"}), 400

        project = ProjectManager.get_project(project_id)
        if not project:
            return jsonify({"success": False, "error": f"Project not found: {project_id}"}), 404

        # Generate ontology without research
        text = ProjectManager.get_extracted_text(project_id)
        document_texts = [text] if text else []

        generator = OntologyGenerator()
        ontology = generator.generate(
            document_texts=document_texts,
            simulation_requirement=project.simulation_requirement or "",
        )

        project.ontology = {
            "entity_types": ontology.get("entity_types", []),
            "edge_types": ontology.get("edge_types", []),
        }
        project.analysis_summary = ontology.get("analysis_summary", "")
        project.research_confirmed = False
        project.status = ProjectStatus.ONTOLOGY_GENERATED
        ProjectManager.save_project(project)

        return jsonify({"success": True, "data": project.to_dict()})

    except Exception as e:
        logger.error(f"Research skip failed: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ============== Graph Data Interface ==============

@graph_bp.route('/data/<graph_id>', methods=['GET'])
def get_graph_data(graph_id: str):
    """
    Get graph data (nodes and edges)
    """
    try:
        storage = _get_storage()
        builder = GraphBuilderService(storage=storage)
        graph_data = builder.get_graph_data(graph_id)

        return jsonify({
            "success": True,
            "data": graph_data
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@graph_bp.route('/delete/<graph_id>', methods=['DELETE'])
def delete_graph(graph_id: str):
    """
    Delete graph
    """
    try:
        storage = _get_storage()
        builder = GraphBuilderService(storage=storage)
        builder.delete_graph(graph_id)

        return jsonify({
            "success": True,
            "message": f"Graph deleted: {graph_id}"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
