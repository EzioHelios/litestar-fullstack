import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/tasks/schedules")({
  component: SchedulesPage,
})

function SchedulesPage() {
  return <PlaceholderPage eyebrow="定时任务" title="定时任务设置" />
}

