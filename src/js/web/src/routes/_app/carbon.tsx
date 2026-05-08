/**
 * 碳管理布局：tabs 导航 + 子路由 Outlet（与 xtck_deploy 页面结构对应）
 */
import { createFileRoute, Link, Outlet, useLocation } from "@tanstack/react-router"

import { cn } from "@/lib/utils"

const TABS = [
  { path: "/carbon", label: "态势总览" },
  { path: "/carbon/page2", label: "视频监控" },
  { path: "/carbon/page3", label: "电能监测" },
  { path: "/carbon/page4", label: "碳能协同" },
  { path: "/carbon/map", label: "地图" },
  { path: "/carbon/hwpm", label: "户外大屏" },
] as const

export const Route = createFileRoute("/_app/carbon")({
  component: CarbonLayout,
})

function CarbonLayout() {
  const location = useLocation()
  const pathname = location.pathname

  return (
    <div className="flex flex-1 flex-col space-y-4">
      <div className="flex items-center gap-2 border-b px-1">
        {TABS.map(({ path, label }) => (
          <Link
            key={path}
            to={path}
            className={cn(
              "px-4 py-2 text-sm font-medium transition-colors hover:text-primary",
              pathname === path || (path === "/carbon" && (pathname === "/carbon" || pathname === "/carbon/"))
                ? "border-b-2 border-primary text-primary"
                : "text-muted-foreground"
            )}
          >
            {label}
          </Link>
        ))}
      </div>
      <Outlet />
    </div>
  )
}

export default CarbonLayout
