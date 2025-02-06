export class Logger {
  public static debug(message: string): void {
    console.log(`[DEBUG] ${message}`);
  }

  public static info(message: string): void {
    console.log(`[INFO] ${message}`);
  }

  public static warning(message: string): void {
    console.warn(`[WARNING] ${message}`);
  }

  public static error(message: string): void {
    console.error(`[ERROR] ${message}`);
  }
}
