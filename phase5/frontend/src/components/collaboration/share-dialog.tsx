"use client";

import { useState } from "react";
import { Loader2, Share2, Trash2, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { UserAvatar } from "./user-avatar";
import { shareApi } from "@/lib/api";
import type { TaskShare } from "@/types/task";

interface ShareDialogProps {
  taskId: string;
  taskTitle: string;
  shares: TaskShare[];
  onSharesChange?: () => void;
  trigger?: React.ReactNode;
}

export function ShareDialog({
  taskId,
  taskTitle,
  shares,
  onSharesChange,
  trigger,
}: ShareDialogProps) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<"view" | "edit">("view");
  const [isLoading, setIsLoading] = useState(false);
  const [removingId, setRemovingId] = useState<string | null>(null);
  const { toast } = useToast();

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsLoading(true);
    try {
      await shareApi.share(taskId, email, permission);
      toast({
        title: "Task shared",
        description: `Shared with ${email}`,
      });
      setEmail("");
      onSharesChange?.();
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Failed to share",
        description: error.message || "Could not share task",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveShare = async (shareId: string) => {
    setRemovingId(shareId);
    try {
      await shareApi.removeShare(taskId, shareId);
      toast({
        title: "Share removed",
        description: "Access has been revoked",
      });
      onSharesChange?.();
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Failed to remove share",
        description: error.message || "Could not remove share",
      });
    } finally {
      setRemovingId(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger || (
          <Button variant="outline" size="sm" className="gap-2">
            <Share2 className="h-4 w-4" />
            Share
          </Button>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            Share Task
          </DialogTitle>
          <DialogDescription>
            Share &quot;{taskTitle}&quot; with other users.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleShare} className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Label htmlFor="email" className="sr-only">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
              />
            </div>
            <Select
              value={permission}
              onValueChange={(v) => setPermission(v as "view" | "edit")}
            >
              <SelectTrigger className="w-24">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="view">View</SelectItem>
                <SelectItem value="edit">Edit</SelectItem>
              </SelectContent>
            </Select>
            <Button type="submit" disabled={isLoading || !email.trim()}>
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <UserPlus className="h-4 w-4" />
              )}
            </Button>
          </div>
        </form>

        {shares.length > 0 && (
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">Shared with</Label>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {shares.map((share) => (
                <div
                  key={share.id}
                  className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                >
                  <div className="flex items-center gap-2">
                    <UserAvatar user={share.shared_with} size="sm" />
                    <div className="text-sm">
                      <p className="font-medium">
                        {share.shared_with.name || share.shared_with.email}
                      </p>
                      <p className="text-xs text-muted-foreground capitalize">
                        {share.permission}
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveShare(share.id)}
                    disabled={removingId === share.id}
                  >
                    {removingId === share.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Trash2 className="h-4 w-4 text-destructive" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        )}

        {shares.length === 0 && (
          <p className="text-sm text-muted-foreground text-center py-4">
            This task hasn&apos;t been shared with anyone yet.
          </p>
        )}
      </DialogContent>
    </Dialog>
  );
}
