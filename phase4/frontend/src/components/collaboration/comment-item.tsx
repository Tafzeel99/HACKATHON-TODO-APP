"use client";

import { useState } from "react";
import { formatDistanceToNow } from "@/lib/utils";
import { Edit2, Loader2, MoreHorizontal, Reply, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { UserAvatar } from "./user-avatar";
import type { Comment } from "@/types/task";

interface CommentItemProps {
  comment: Comment;
  currentUserId: string;
  onEdit?: (commentId: string, content: string) => Promise<void>;
  onDelete?: (commentId: string) => Promise<void>;
  onReply?: (parentId: string, content: string) => Promise<void>;
  depth?: number;
}

export function CommentItem({
  comment,
  currentUserId,
  onEdit,
  onDelete,
  onReply,
  depth = 0,
}: CommentItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isReplying, setIsReplying] = useState(false);
  const [editContent, setEditContent] = useState(comment.content);
  const [replyContent, setReplyContent] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const isOwner = comment.user.id === currentUserId;
  const maxDepth = 3;

  const handleSaveEdit = async () => {
    if (!editContent.trim() || !onEdit) return;
    setIsLoading(true);
    try {
      await onEdit(comment.id, editContent);
      setIsEditing(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmitReply = async () => {
    if (!replyContent.trim() || !onReply) return;
    setIsLoading(true);
    try {
      await onReply(comment.id, replyContent);
      setReplyContent("");
      setIsReplying(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!onDelete) return;
    setIsLoading(true);
    try {
      await onDelete(comment.id);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={depth > 0 ? "ml-8 border-l-2 border-muted pl-4" : ""}>
      <div className="flex gap-3 py-3">
        <UserAvatar user={comment.user} size="sm" showTooltip={false} />

        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {comment.user.name || comment.user.email}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(comment.created_at)}
              </span>
              {comment.updated_at !== comment.created_at && (
                <span className="text-xs text-muted-foreground">(edited)</span>
              )}
            </div>

            {isOwner && !isEditing && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setIsEditing(true)}>
                    <Edit2 className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={handleDelete}
                    className="text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>

          {isEditing ? (
            <div className="mt-2 space-y-2">
              <Textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                rows={2}
                disabled={isLoading}
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSaveEdit}
                  disabled={isLoading || !editContent.trim()}
                >
                  {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setIsEditing(false);
                    setEditContent(comment.content);
                  }}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <p className="text-sm mt-1 whitespace-pre-wrap">{comment.content}</p>
          )}

          {!isEditing && depth < maxDepth && onReply && (
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 mt-1 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => setIsReplying(!isReplying)}
            >
              <Reply className="h-3 w-3 mr-1" />
              Reply
            </Button>
          )}

          {isReplying && (
            <div className="mt-2 space-y-2">
              <Textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Write a reply..."
                rows={2}
                disabled={isLoading}
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={handleSubmitReply}
                  disabled={isLoading || !replyContent.trim()}
                >
                  {isLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                  Reply
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => {
                    setIsReplying(false);
                    setReplyContent("");
                  }}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Nested replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="space-y-0">
          {comment.replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              currentUserId={currentUserId}
              onEdit={onEdit}
              onDelete={onDelete}
              onReply={onReply}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}
