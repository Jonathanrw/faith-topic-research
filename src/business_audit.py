from src.business_status_report import main as business_status_main
from src.funnel_generator import main as funnel_main
from src.live_link_audit import main as live_link_audit_main
from src.monetization_summary import main as monetization_summary_main
from src.offer_usage_report import main as offer_usage_main
from src.prelaunch_check import main as prelaunch_check_main
from src.product_catalog_report import main as product_catalog_main
from src.revenue_readiness_report import main as revenue_readiness_main


def main() -> None:
    product_catalog_main()
    funnel_main()
    offer_usage_main()
    monetization_summary_main()
    revenue_readiness_main()
    live_link_audit_main()
    business_status_main()
    prelaunch_check_main()

    print("Business audit complete.")


if __name__ == "__main__":
    main()
