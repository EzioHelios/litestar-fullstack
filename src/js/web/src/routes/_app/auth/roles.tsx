import { createFileRoute } from "@tanstack/react-router"
import { PlaceholderPage } from "@/components/platform/placeholder-page"

export const Route = createFileRoute("/_app/auth/roles")({
  component: RolesManagePage,
})

function RolesManagePage() {
  return <PlaceholderPage eyebrow="权限管理" title="角色管理" />
}

