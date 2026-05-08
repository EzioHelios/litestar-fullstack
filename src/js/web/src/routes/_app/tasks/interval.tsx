import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/tasks/interval")({
  component: IntervalPage,
})

function IntervalPage() {
  return <PlaceholderPage eyebrow="定时任务" title="时间间隔设置" />
}

