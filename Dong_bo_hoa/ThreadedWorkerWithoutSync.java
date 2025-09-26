public class ThreadedWorkerWithoutSync extends Thread {
    ResourcesExploiter rExp;
    public ThreadedWorkerWithoutSync(ResourcesExploiter rExp) {
        this.rExp = rExp;
    }
    public void run() {
        for (int i = 0; i < 1000; i++) {
            rExp.exploit();
        }
    }
    public static void main(String[] args) throws InterruptedException {
        ResourcesExploiter rExp = new ResourcesExploiter(0);
        ThreadedWorkerWithoutSync worker1 = new ThreadedWorkerWithoutSync(rExp);
        ThreadedWorkerWithoutSync worker2 = new ThreadedWorkerWithoutSync(rExp);
        ThreadedWorkerWithoutSync worker3 = new ThreadedWorkerWithoutSync(rExp);
        worker1.start();
        worker2.start();
        worker3.start();
        worker1.join();
        worker2.join();
        worker3.join();
        System.out.println("Final rExp value: " + rExp.getRsc());
    }
}
