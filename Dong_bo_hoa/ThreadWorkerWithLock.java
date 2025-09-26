public class ThreadWorkerWithLock extends Thread {
    ResourcesExploiterWithLock rExp;
    public ThreadWorkerWithLock(ResourcesExploiterWithLock rExp) {
        this.rExp = rExp;
    }
    public void run() {
        for (int i = 0; i < 1000; i++) {
            rExp.exploit();
        }
    }
    public static void main(String[] args) throws InterruptedException {
        ResourcesExploiterWithLock rExp = new ResourcesExploiterWithLock(0);
        ThreadWorkerWithLock worker1 = new ThreadWorkerWithLock(rExp);
        ThreadWorkerWithLock worker2 = new ThreadWorkerWithLock(rExp);
        ThreadWorkerWithLock worker3 = new ThreadWorkerWithLock(rExp);
        worker1.start();
        worker2.start();
        worker3.start();
        worker1.join();
        worker2.join();
        worker3.join();
        System.out.println("Final rExp value: " + rExp.getRsc());
    }
}
