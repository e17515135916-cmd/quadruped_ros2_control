"""
Command-line interface for the presentation visualization system.
"""

import argparse
import sys
from pathlib import Path
from .config_manager import ConfigManager
from .logger import setup_logger


def main():
    """
    Main entry point for the CLI.
    """
    parser = argparse.ArgumentParser(
        description="Presentation Visualization System - Generate professional robotics visualizations"
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Run all visualization modules in batch mode'
    )
    
    parser.add_argument(
        '--module',
        type=str,
        choices=[
            'kinematic_diagram',
            'workspace_analysis',
            'ros_graph',
            'fsm_visualization',
            'keyframe_extraction',
            'plot_generation'
        ],
        help='Run a specific visualization module'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Override output directory'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--generate-config',
        action='store_true',
        help='Generate a template configuration file'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    logger = setup_logger(level=log_level)
    
    # Generate config template if requested
    if args.generate_config:
        template_path = Path(__file__).parent / 'config_template.yaml'
        output_path = Path('config.yaml')
        
        if output_path.exists():
            logger.warning(f"Configuration file already exists: {output_path}")
            response = input("Overwrite? (y/n): ")
            if response.lower() != 'y':
                logger.info("Aborted")
                return 0
        
        import shutil
        shutil.copy(template_path, output_path)
        logger.info(f"Generated configuration template: {output_path}")
        return 0
    
    # Load configuration
    logger.info(f"Loading configuration from: {args.config}")
    config = ConfigManager(args.config)
    
    # Override output directory if specified
    if args.output:
        config.config['output']['directory'] = args.output
        logger.info(f"Output directory overridden: {args.output}")
    
    # Display configuration summary
    output_config = config.get_output_config()
    style = config.get_style()
    logger.info(f"Output directory: {output_config['directory']}")
    logger.info(f"Output format: {output_config['format']}")
    logger.info(f"DPI: {style['dpi']}")
    
    # Execute requested operation
    if args.batch:
        logger.info("Batch mode not yet implemented")
        logger.info("This will execute all visualization modules in sequence")
        return 1
    elif args.module:
        logger.info(f"Module '{args.module}' not yet implemented")
        return 1
    else:
        parser.print_help()
        return 0


if __name__ == '__main__':
    sys.exit(main())
