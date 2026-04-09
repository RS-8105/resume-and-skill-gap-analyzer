package com.example.resumeanalyzer.service; // <-- change if needed

import com.example.resumeanalyzer.dto.AnalysisResponse;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class NlpService {

    private final RestTemplate restTemplate = new RestTemplate();

    @org.springframework.beans.factory.annotation.Value("${NLP_SERVICE_URL:http://localhost:8000/analyze}")
    private String nlpServiceUrl;

    public AnalysisResponse analyzeResume(String resumeText, String company, String jobDescription) {

        String url = nlpServiceUrl;

        Map<String, String> request = new HashMap<>();
        request.put("resume_text", resumeText);
        request.put("company", company);
        request.put("job_description", jobDescription);

        try {
            return restTemplate.postForObject(url, request, AnalysisResponse.class);
        } catch (RestClientException e) {
            AnalysisResponse errorResponse = new AnalysisResponse();
            errorResponse.setError("Failed to connect to Python NLP service: " + e.getMessage());
            return errorResponse;
        }
    }
}