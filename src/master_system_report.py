from src.business_audit import main as business_audit_main
from src.final_readiness_report import main as final_readiness_main
from src.launch_packet import main as launch_packet_main


def main() -> None:
    business_audit_main()
    launch_packet_main()
    final_readiness_main()
    print("Master system report complete.")


if __name__ == "__main__":
    main()
