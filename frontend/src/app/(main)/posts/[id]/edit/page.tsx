'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { postsApi } from '@/lib/api';
import { useAuthStore } from '@/stores/authStore';
import type { Post } from '@/types';

const postSchema = z.object({
  title: z.string().min(1, '제목을 입력해주세요').max(200, '제목은 200자 이내로 입력해주세요'),
  content: z.string().min(1, '내용을 입력해주세요'),
  is_published: z.boolean(),
});

type PostForm = z.infer<typeof postSchema>;

export default function EditPostPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const postId = Number(params.id);

  const [post, setPost] = useState<Post | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PostForm>({
    resolver: zodResolver(postSchema),
  });

  useEffect(() => {
    const fetchPost = async () => {
      try {
        const postData = await postsApi.getById(postId);
        setPost(postData);
        reset({
          title: postData.title,
          content: postData.content,
          is_published: postData.is_published,
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : '게시글을 불러오는데 실패했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchPost();
  }, [postId, reset]);

  const onSubmit = async (data: PostForm) => {
    setError(null);
    try {
      await postsApi.update(postId, data);
      router.push(`/posts/${postId}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : '게시글 수정에 실패했습니다.';
      setError(message);
    }
  };

  // 권한 확인
  const canEdit = user && post && (user.id === post.author.id || user.role === 'admin');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="space-y-4">
        <Link href="/posts">
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            목록으로
          </Button>
        </Link>
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          {error || '게시글을 찾을 수 없습니다.'}
        </div>
      </div>
    );
  }

  if (!canEdit) {
    return (
      <div className="space-y-4">
        <Link href={`/posts/${postId}`}>
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </Link>
        <div className="p-4 text-red-500 bg-red-50 dark:bg-red-950 rounded-lg">
          수정 권한이 없습니다.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href={`/posts/${postId}`}>
          <Button variant="ghost">
            <ArrowLeft className="mr-2 h-4 w-4" />
            돌아가기
          </Button>
        </Link>
        <h1 className="text-2xl font-bold">게시글 수정</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>게시글 수정</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 dark:bg-red-950 rounded-md">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="title">제목</Label>
              <Input
                id="title"
                placeholder="게시글 제목을 입력하세요"
                {...register('title')}
                disabled={isSubmitting}
              />
              {errors.title && (
                <p className="text-sm text-red-500">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="content">내용</Label>
              <textarea
                id="content"
                placeholder="게시글 내용을 입력하세요"
                className="flex min-h-[300px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                {...register('content')}
                disabled={isSubmitting}
              />
              {errors.content && (
                <p className="text-sm text-red-500">{errors.content.message}</p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_published"
                {...register('is_published')}
                className="h-4 w-4 rounded border-gray-300"
                disabled={isSubmitting}
              />
              <Label htmlFor="is_published">공개</Label>
            </div>

            <div className="flex gap-2">
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                수정하기
              </Button>
              <Link href={`/posts/${postId}`}>
                <Button type="button" variant="outline">
                  취소
                </Button>
              </Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
