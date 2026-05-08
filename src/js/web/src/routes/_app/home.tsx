import { useQuery } from "@tanstack/react-query"
import { createFileRoute, Link } from "@tanstack/react-router"
import { ChevronRight, Plus, Settings, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PageContainer, PageHeader, PageSection } from "@/components/ui/page-layout"
import { useAuthStore } from "@/lib/auth"
import { listTeams } from "@/lib/generated/api"

export const Route = createFileRoute("/_app/home")({
  component: HomePage,
})

function HomePage() {
  const user = useAuthStore((state) => state.user)
  const { data: teams = [] } = useQuery({
    queryKey: ["teams"],
    queryFn: async () => {
      const response = await listTeams()
      return response.data?.items ?? []
    },
  })

  const displayName = user?.name || user?.email?.split("@")[0] || "there"

  return (
    <PageContainer className="flex-1 space-y-8">
      <PageHeader
        eyebrow="工作台"
        title={`欢迎回来，${displayName}`}
        description="管理您的团队并探索平台功能。"
        actions={
          <Button size="sm" asChild>
            <Link to="/teams/new">
              <Plus className="mr-2 h-4 w-4" /> 创建团队
            </Link>
          </Button>
        }
      />

      <PageSection delay={0.1}>
        <div className="flex gap-6">
          <Card hover className="min-w-0 flex-1">
            <CardHeader className="space-y-1">
              <CardTitle className="text-lg">您的团队</CardTitle>
              <CardDescription>您所属的团队</CardDescription>
            </CardHeader>
            <CardContent>
              {teams.length > 0 ? (
                <div className="space-y-2">
                  {teams.slice(0, 3).map((team) => (
                    <Link
                      key={team.id}
                      to="/teams/$teamId"
                      params={{ teamId: team.id }}
                      className="flex items-center gap-2 rounded-lg border border-border/60 bg-background/60 p-3 transition-colors hover:bg-accent"
                    >
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{team.name}</span>
                    </Link>
                  ))}
                  {teams.length > 3 && (
                    <Link to="/teams" className="block text-center text-sm text-muted-foreground hover:text-foreground">
                      查看全部 {teams.length} 个团队
                    </Link>
                  )}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted-foreground text-sm mb-3">您还未加入任何团队。</p>
                  <Button asChild size="sm" variant="outline">
                    <Link to="/teams/new">创建您的第一个团队</Link>
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="h-fit w-72 shrink-0 border-border/40 bg-linear-to-br from-muted/30 to-muted/10">
            <CardHeader className="space-y-1 pb-3">
              <CardTitle className="text-lg">快捷操作</CardTitle>
              <CardDescription>常用任务</CardDescription>
            </CardHeader>
            <CardContent className="space-y-1.5">
              <Link to="/teams/new" className="group flex items-center gap-3 rounded-lg bg-background/60 p-3 transition-all hover:bg-background hover:shadow-sm">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <Plus className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">创建新团队</p>
                  <p className="text-xs text-muted-foreground">开始协作</p>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
              </Link>
              <Link to="/profile" className="group flex items-center gap-3 rounded-lg bg-background/60 p-3 transition-all hover:bg-background hover:shadow-sm">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-orange-500/10 text-orange-600 transition-colors group-hover:bg-orange-500 group-hover:text-white dark:text-orange-400">
                  <Settings className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">编辑个人资料</p>
                  <p className="text-xs text-muted-foreground">管理账号设置</p>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
              </Link>
              <Link to="/teams" className="group flex items-center gap-3 rounded-lg bg-background/60 p-3 transition-all hover:bg-background hover:shadow-sm">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-500/10 text-blue-600 transition-colors group-hover:bg-blue-500 group-hover:text-white dark:text-blue-400">
                  <Users className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm">浏览所有团队</p>
                  <p className="text-xs text-muted-foreground">查看您的工作空间</p>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground/50 transition-transform group-hover:translate-x-0.5 group-hover:text-foreground" />
              </Link>
            </CardContent>
          </Card>
        </div>
      </PageSection>
    </PageContainer>
  )
}
