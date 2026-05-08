import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/data/api-key-mapping")({
  component: ApiKeyMappingPage,
})

function ApiKeyMappingPage() {
  return <PlaceholderPage eyebrow="数据管理" title="接口结果key映射" />
}

