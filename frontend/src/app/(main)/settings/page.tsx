'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Loader2, Moon, Sun, Monitor } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAuthStore } from '@/stores/authStore';
import { useThemeStore } from '@/stores/themeStore';
import { usersApi } from '@/lib/api';

const profileSchema = z.object({
  email: z.string().email('올바른 이메일 형식을 입력해주세요'),
  username: z
    .string()
    .min(3, '사용자명은 최소 3자 이상이어야 합니다')
    .regex(/^[a-zA-Z][a-zA-Z0-9_]*$/, '사용자명은 영문으로 시작해야 합니다'),
  full_name: z.string().optional(),
});

const passwordSchema = z.object({
  currentPassword: z.string().min(1, '현재 비밀번호를 입력해주세요'),
  newPassword: z
    .string()
    .min(8, '비밀번호는 최소 8자 이상이어야 합니다')
    .regex(/[A-Z]/, '대문자가 최소 1개 포함되어야 합니다')
    .regex(/[a-z]/, '소문자가 최소 1개 포함되어야 합니다')
    .regex(/\d/, '숫자가 최소 1개 포함되어야 합니다'),
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: '비밀번호가 일치하지 않습니다',
  path: ['confirmPassword'],
});

type ProfileForm = z.infer<typeof profileSchema>;
type PasswordForm = z.infer<typeof passwordSchema>;

export default function SettingsPage() {
  const { user, fetchUser } = useAuthStore();
  const { theme, setTheme } = useThemeStore();
  const [profileError, setProfileError] = useState<string | null>(null);
  const [profileSuccess, setProfileSuccess] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const profileForm = useForm<ProfileForm>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      email: user?.email || '',
      username: user?.username || '',
      full_name: user?.full_name || '',
    },
  });

  const passwordForm = useForm<PasswordForm>({
    resolver: zodResolver(passwordSchema),
    defaultValues: {
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    },
  });

  const onProfileSubmit = async (data: ProfileForm) => {
    if (!user) return;
    setProfileError(null);
    setProfileSuccess(false);

    try {
      await usersApi.update(user.id, data);
      await fetchUser();
      setProfileSuccess(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : '프로필 업데이트에 실패했습니다.';
      setProfileError(message);
    }
  };

  const onPasswordSubmit = async (data: PasswordForm) => {
    if (!user) return;
    setPasswordError(null);
    setPasswordSuccess(false);

    try {
      await usersApi.update(user.id, { password: data.newPassword });
      passwordForm.reset();
      setPasswordSuccess(true);
    } catch (err) {
      const message = err instanceof Error ? err.message : '비밀번호 변경에 실패했습니다.';
      setPasswordError(message);
    }
  };

  const themeOptions = [
    { value: 'light', label: '라이트', icon: Sun },
    { value: 'dark', label: '다크', icon: Moon },
    { value: 'system', label: '시스템', icon: Monitor },
  ] as const;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">설정</h1>
        <p className="text-muted-foreground">계정 및 앱 설정을 관리하세요</p>
      </div>

      <Tabs defaultValue="profile" className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">프로필</TabsTrigger>
          <TabsTrigger value="password">비밀번호</TabsTrigger>
          <TabsTrigger value="appearance">화면 설정</TabsTrigger>
        </TabsList>

        {/* 프로필 탭 */}
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle>프로필 정보</CardTitle>
              <CardDescription>기본 프로필 정보를 수정하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-4">
                {profileError && (
                  <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-950 rounded-md">
                    {profileError}
                  </div>
                )}
                {profileSuccess && (
                  <div className="p-3 text-sm text-green-500 bg-green-50 dark:bg-green-950 rounded-md">
                    프로필이 업데이트되었습니다.
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email">이메일</Label>
                  <Input
                    id="email"
                    type="email"
                    {...profileForm.register('email')}
                    disabled={profileForm.formState.isSubmitting}
                  />
                  {profileForm.formState.errors.email && (
                    <p className="text-sm text-red-500">{profileForm.formState.errors.email.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="username">사용자명</Label>
                  <Input
                    id="username"
                    {...profileForm.register('username')}
                    disabled={profileForm.formState.isSubmitting}
                  />
                  {profileForm.formState.errors.username && (
                    <p className="text-sm text-red-500">{profileForm.formState.errors.username.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="full_name">이름</Label>
                  <Input
                    id="full_name"
                    {...profileForm.register('full_name')}
                    disabled={profileForm.formState.isSubmitting}
                  />
                </div>

                <Button type="submit" disabled={profileForm.formState.isSubmitting}>
                  {profileForm.formState.isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  저장
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 비밀번호 탭 */}
        <TabsContent value="password">
          <Card>
            <CardHeader>
              <CardTitle>비밀번호 변경</CardTitle>
              <CardDescription>계정 비밀번호를 변경하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
                {passwordError && (
                  <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-950 rounded-md">
                    {passwordError}
                  </div>
                )}
                {passwordSuccess && (
                  <div className="p-3 text-sm text-green-500 bg-green-50 dark:bg-green-950 rounded-md">
                    비밀번호가 변경되었습니다.
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="currentPassword">현재 비밀번호</Label>
                  <Input
                    id="currentPassword"
                    type="password"
                    {...passwordForm.register('currentPassword')}
                    disabled={passwordForm.formState.isSubmitting}
                  />
                  {passwordForm.formState.errors.currentPassword && (
                    <p className="text-sm text-red-500">{passwordForm.formState.errors.currentPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="newPassword">새 비밀번호</Label>
                  <Input
                    id="newPassword"
                    type="password"
                    {...passwordForm.register('newPassword')}
                    disabled={passwordForm.formState.isSubmitting}
                  />
                  {passwordForm.formState.errors.newPassword && (
                    <p className="text-sm text-red-500">{passwordForm.formState.errors.newPassword.message}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">새 비밀번호 확인</Label>
                  <Input
                    id="confirmPassword"
                    type="password"
                    {...passwordForm.register('confirmPassword')}
                    disabled={passwordForm.formState.isSubmitting}
                  />
                  {passwordForm.formState.errors.confirmPassword && (
                    <p className="text-sm text-red-500">{passwordForm.formState.errors.confirmPassword.message}</p>
                  )}
                </div>

                <Button type="submit" disabled={passwordForm.formState.isSubmitting}>
                  {passwordForm.formState.isSubmitting && (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  )}
                  변경
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 화면 설정 탭 */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>화면 설정</CardTitle>
              <CardDescription>테마와 화면 옵션을 설정하세요</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label>테마</Label>
                  <div className="grid grid-cols-3 gap-4 mt-2">
                    {themeOptions.map((option) => {
                      const Icon = option.icon;
                      return (
                        <button
                          key={option.value}
                          type="button"
                          onClick={() => setTheme(option.value)}
                          className={`flex flex-col items-center gap-2 p-4 rounded-lg border-2 transition-colors ${
                            theme === option.value
                              ? 'border-primary bg-primary/10'
                              : 'border-muted hover:border-primary/50'
                          }`}
                        >
                          <Icon className="h-6 w-6" />
                          <span className="text-sm font-medium">{option.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
