'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MainLayout } from '@/components/layout';
import { useAuthStore } from '@/stores/authStore';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && (!user || user.role !== 'admin')) {
      router.push('/dashboard');
    }
  }, [user, isLoading, router]);

  // 로딩 중이거나 권한 체크 중
  if (isLoading) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center h-64">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
        </div>
      </MainLayout>
    );
  }

  // 권한 없음
  if (!user || user.role !== 'admin') {
    return (
      <MainLayout>
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          관리자 권한이 필요합니다.
        </div>
      </MainLayout>
    );
  }

  return <MainLayout>{children}</MainLayout>;
}
