import { type SystemSettings } from '@/types';

export const systemSettings = $state<SystemSettings>({
    notificationPermissionGranted: false,
    appDataDirPath: '',
});
