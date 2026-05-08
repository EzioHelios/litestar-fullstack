import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/alarm-events")({
  component: AlarmEventsPage,
})

function AlarmEventsPage() {
  return <PlaceholderPage eyebrow="数据管理" title="预警事件" />
}

