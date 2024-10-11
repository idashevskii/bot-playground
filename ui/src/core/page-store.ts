import { remove } from '@/utils/collections';
import { defineStore } from 'pinia';

let popupLastId = 0;
let popupMsgId = 0;
const AUTO_CONFIRM_TIMEOUT = 60 * 1000;

export interface Confirmation {
  id: number;
  question: string;
  autoConfirm: boolean;
  resolve: (res: boolean) => void;
}

export interface Notification {
  id: number;
  message: string;
  color: string;
}

export const usePageStore = defineStore('page', {
  state: () => ({
    title: '',
    autoConfirmActive: false,
    confirmations: [] as Confirmation[],
    notifications: [] as Notification[],
  }),
  actions: {
    setTitle(title: string) {
      this.title = title;
    },
    notifyException(ex: unknown) {
      this.notifications.push({ id: ++popupMsgId, message: String(ex), color: 'error' });
    },
    markNotificationViewed(notification: Notification){
      remove(this.notifications, 'id', notification.id);
    },
    async confirm(question: string): Promise<boolean> {
      if (this.autoConfirmActive) {
        return true;
      }
      return new Promise((resolve) => {
        this.confirmations.push({
          id: ++popupLastId,
          autoConfirm: false,
          question,
          resolve,
        });
      });
    },
    setConfirmed(item: Confirmation, confirmed: boolean) {
      remove(this.confirmations, 'id', item.id);
      if (confirmed && item.autoConfirm) {
        this.autoConfirmActive = true;
        setTimeout(() => {
          // console.log('Auto confirm disabled');
          this.autoConfirmActive = false;
        }, AUTO_CONFIRM_TIMEOUT);
      }
      item.resolve(confirmed);
    },
  },
});
