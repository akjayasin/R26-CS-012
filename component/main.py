from pipeline_controller import PipelineController


def main():
    """
    Entry point for the PP1 standalone middleware prototype.
    """
    controller = PipelineController()
    summary = controller.run()

    print("\n==============================")
    print("CPSM Middleware Demo Completed")
    print("==============================")
    print(f"Pipeline Status     : {summary.get('pipeline_status')}")
    print(f"Processed Files     : {summary.get('processed_files')}")
    print(f"Successful Files    : {summary.get('successful_files')}")
    print(f"Failed Files        : {summary.get('failed_files')}")
    print("\nCheck these folders:")
    print("- outputs/structured_outputs")
    print("- outputs/evaluation")
    print("- outputs/logs")


if __name__ == "__main__":
    main()