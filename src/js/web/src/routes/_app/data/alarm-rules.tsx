import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/alarm-rules")({
  component: AlarmRulesPage,
})

function AlarmRulesPage() {
  return <PlaceholderPage eyebrow="数据管理" title="预警规则" />
}

