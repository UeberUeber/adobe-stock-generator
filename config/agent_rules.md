# Agent Explicit Rules (Metadata Generation)

> [!CAUTION]
> **ABSOLUTE RULE FOR AGENT (ANTIGRAVITY):**
> You must **NEVER** use Python automation scripts (e.g., `ai_metadata_generator.py`, `update_json_metadata.py`, etc.) to generate, analyze, or process image metadata.

## Required Workflow for Metadata Generation
Whenever tasked with analyzing generated images and creating JSON metadata, you must follow this exact manual process:

1. Use the `view_file` tool to directly view each generated image.
2. Analyze the image visually and construct a 25-35 keyword list based on the mandated attributes (Objects, Location, Mood, Colors, Lighting, Composition).
3. Use the `write_to_file` tool to write or overwrite the `.json` file for that image based on your direct visual analysis.

**Any deviation from this manual verification and typing process is a critical system violation.**
