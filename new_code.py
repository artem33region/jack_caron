import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Date;
import java.util.Timer;
import java.util.TimerTask;
import java.util.concurrent.atomic.AtomicInteger;

public class CrptApi {

    private final int requestLimit;
    private final long timeInterval;
    private final AtomicInteger requestCount = new AtomicInteger(0);
    private final HttpClient httpClient = HttpClients.createDefault();

    public CrptApi(int requestLimit, TimeUnit timeUnit) {
        this.requestLimit = requestLimit;
        this.timeInterval = timeUnit.toMillis(1);
        scheduleRequestLimitReset();
    }

    public void createDocument(String document, String signature) throws IOException, InterruptedException {
        if (requestCount.get() >= requestLimit) {
            Thread.sleep(timeInterval); // wait until the request limit resets
        }

        HttpPost request = new HttpPost("https://ismp.crpt.ru/api/v3/lk/documents/create");
        request.addHeader("Content-Type", "application/json");

        StringEntity params = new StringEntity(document);
        request.setEntity(params);

        HttpResponse response = httpClient.execute(request);
        HttpEntity entity = response.getEntity();

        if (entity != null) {
            try (BufferedReader in = new BufferedReader(new InputStreamReader(entity.getContent()))) {
                String result = in.lines().reduce("", String::concat);
                System.out.println(result);
            }
        }

        requestCount.incrementAndGet();
    }

    private void scheduleRequestLimitReset() {
        Timer timer = new Timer();
        timer.schedule(new TimerTask() {
            @Override
            public void run() {
                requestCount.set(0);
            }
        }, new Date(), timeInterval);
    }
}
