'use client';

import { useEffect, useState } from 'react';
import { Users, FileText, MessageSquare, TrendingUp, PenSquare, MessagesSquare } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { dashboardApi } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import type { User, DashboardStats } from '@/types';

interface RecentPost {
  id: number;
  title: string;
  author_username: string;
  view_count: number;
  comment_count: number;
  created_at: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentUsers, setRecentUsers] = useState<User[]>([]);
  const [recentPosts, setRecentPosts] = useState<RecentPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 기본 통계 가져오기
        const statsData = await dashboardApi.getStats();
        setStats(statsData);

        // 최근 게시글 가져오기
        try {
          const postsData = await dashboardApi.getRecentPosts(5) as RecentPost[];
          setRecentPosts(postsData);
        } catch {
          // 에러 무시
        }

        // 관리자인 경우 최근 사용자도 가져오기
        if (user?.role === 'admin') {
          try {
            const usersData = await dashboardApi.getRecentUsers() as User[];
            setRecentUsers(usersData);
          } catch {
            // 권한 없으면 무시
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '데이터를 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
        {error}
      </div>
    );
  }

  // 관리자용 통계 카드
  const adminStatCards = [
    {
      title: '전체 사용자',
      value: stats?.total_users || 0,
      icon: Users,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: '전체 게시글',
      value: stats?.total_posts || 0,
      icon: FileText,
      color: 'text-green-500',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      title: '전체 댓글',
      value: stats?.total_comments || 0,
      icon: MessageSquare,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
    {
      title: '오늘 가입',
      value: stats?.users_today || 0,
      icon: TrendingUp,
      color: 'text-orange-500',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
  ];

  // 일반 사용자용 통계 카드
  const userStatCards = [
    {
      title: '내 게시글',
      value: stats?.my_posts || 0,
      icon: PenSquare,
      color: 'text-blue-500',
      bgColor: 'bg-blue-100 dark:bg-blue-900',
    },
    {
      title: '내 댓글',
      value: stats?.my_comments || 0,
      icon: MessagesSquare,
      color: 'text-green-500',
      bgColor: 'bg-green-100 dark:bg-green-900',
    },
    {
      title: '전체 게시글',
      value: stats?.total_posts || 0,
      icon: FileText,
      color: 'text-purple-500',
      bgColor: 'bg-purple-100 dark:bg-purple-900',
    },
    {
      title: '오늘 게시글',
      value: stats?.posts_today || 0,
      icon: TrendingUp,
      color: 'text-orange-500',
      bgColor: 'bg-orange-100 dark:bg-orange-900',
    },
  ];

  const statCards = isAdmin ? adminStatCards : userStatCards;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">대시보드</h1>
        <p className="text-muted-foreground">
          {isAdmin ? '서비스 현황을 한눈에 확인하세요' : '나의 활동 현황을 확인하세요'}
        </p>
      </div>

      {/* 통계 카드 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <div className={`p-2 rounded-full ${stat.bgColor}`}>
                  <Icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* 최근 활동 */}
      <div className={`grid gap-4 ${isAdmin ? 'md:grid-cols-2' : 'md:grid-cols-1'}`}>
        {/* 최근 사용자 - 관리자만 표시 */}
        {isAdmin && (
          <Card>
            <CardHeader>
              <CardTitle>최근 가입 사용자</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentUsers.length > 0 ? (
                  recentUsers.map((recentUser) => (
                    <div key={recentUser.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{recentUser.username}</p>
                        <p className="text-sm text-muted-foreground">{recentUser.email}</p>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {new Date(recentUser.created_at).toLocaleDateString('ko-KR')}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="text-muted-foreground">최근 가입한 사용자가 없습니다.</p>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* 최근 게시글 */}
        <Card>
          <CardHeader>
            <CardTitle>최근 게시글</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentPosts.length > 0 ? (
                recentPosts.map((post) => (
                  <div key={post.id} className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{post.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {post.author_username}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground ml-2">
                      {new Date(post.created_at).toLocaleDateString('ko-KR')}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">최근 작성된 게시글이 없습니다.</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
