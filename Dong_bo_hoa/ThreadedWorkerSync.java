public class ThreadedWorkerSync extends Thread {
    final ResourcesExploiter rExp;
    public ThreadedWorkerSync(ResourcesExploiter rExp) {
        this.rExp = rExp;
    }
    public void run() {
        synchronized (rExp) {
            for (int i = 0; i < 1000; i++) {
                rExp.exploit();
            }
        }

    }
    public static void main(String[] args) throws InterruptedException {
        ResourcesExploiter rExp = new ResourcesExploiter(0);
        ThreadedWorkerSync worker1 = new ThreadedWorkerSync(rExp);
        ThreadedWorkerSync worker2 = new ThreadedWorkerSync(rExp);
        ThreadedWorkerSync worker3 = new ThreadedWorkerSync(rExp);
        worker1.start();
        worker2.start();
        worker3.start();
        worker1.join();
        worker2.join();
        worker3.join();
        System.out.println("Final resource value: " + rExp.getRsc());
    }
}
