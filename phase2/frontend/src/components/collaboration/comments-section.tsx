"use client";

import { useState } from "react";
import { Loader2, MessageSquare, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import { CommentItem } from "./comment-item";
import { commentApi } from "@/lib/api";
import type { Comment } from "@/types/task";

interface CommentsSectionProps {
  taskId: string;
  comments: Comment[];
  currentUserId: string;
  onCommentsChange?: () => void;
  maxHeight?: string;
}

export function CommentsSection({
  taskId,
  comments,
  currentUserId,
  onCommentsChange,
  maxHeight = "400px",
}: CommentsSectionProps) {
  const [newComment, setNewComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    setIsSubmitting(true);
    try {
      await commentApi.create(taskId, newComment);
      setNewComment("");
      onCommentsChange?.();
      toast({
        title: "Comment added",
        description: "Your comment has been posted",
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to add comment",
        description: error instanceof Error ? error.message : "Could not post comment",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEdit = async (commentId: string, content: string) => {
    try {
      await commentApi.update(commentId, content);
      onCommentsChange?.();
      toast({ title: "Comment updated" });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to update comment",
        description: error instanceof Error ? error.message : "Could not update comment",
      });
      throw error;
    }
  };

  const handleDelete = async (commentId: string) => {
    try {
      await commentApi.delete(commentId);
      onCommentsChange?.();
      toast({ title: "Comment deleted" });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to delete comment",
        description: error instanceof Error ? error.message : "Could not delete comment",
      });
      throw error;
    }
  };

  const handleReply = async (parentId: string, content: string) => {
    try {
      await commentApi.create(taskId, content, parentId);
      onCommentsChange?.();
      toast({ title: "Reply added" });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Failed to add reply",
        description: error instanceof Error ? error.message : "Could not post reply",
      });
      throw error;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <MessageSquare className="h-5 w-5" />
        <h3 className="font-semibold">
          Comments {comments.length > 0 && `(${comments.length})`}
        </h3>
      </div>

      {/* Comment input */}
      <form onSubmit={handleSubmit} className="space-y-2">
        <Textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Write a comment..."
          rows={2}
          disabled={isSubmitting}
        />
        <div className="flex justify-end">
          <Button
            type="submit"
            size="sm"
            disabled={isSubmitting || !newComment.trim()}
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Send className="h-4 w-4 mr-2" />
            )}
            Post Comment
          </Button>
        </div>
      </form>

      <Separator />

      {/* Comments list */}
      {comments.length > 0 ? (
        <ScrollArea style={{ maxHeight }}>
          <div className="space-y-0 divide-y">
            {comments.map((comment) => (
              <CommentItem
                key={comment.id}
                comment={comment}
                currentUserId={currentUserId}
                onEdit={handleEdit}
                onDelete={handleDelete}
                onReply={handleReply}
              />
            ))}
          </div>
        </ScrollArea>
      ) : (
        <p className="text-sm text-muted-foreground text-center py-8">
          No comments yet. Be the first to comment!
        </p>
      )}
    </div>
  );
}
