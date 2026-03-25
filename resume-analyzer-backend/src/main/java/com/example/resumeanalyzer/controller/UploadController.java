package com.example.resumeanalyzer.controller; // <-- change if needed

import com.example.resumeanalyzer.dto.AnalysisResponse;
import com.example.resumeanalyzer.service.NlpService;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@CrossOrigin(origins = "*")
@RestController
public class UploadController {

    @Autowired
    private NlpService nlpService;

    @PostMapping("/upload")
    public ResponseEntity<AnalysisResponse> uploadFile(
            @RequestParam("file") MultipartFile file,
            @RequestParam("company") String company,
            @RequestParam("jobDescription") String jobDescription) {

        AnalysisResponse response = new AnalysisResponse();

        String text;
        try {
            // Extract text from PDF
            PDDocument document = PDDocument.load(file.getInputStream());
            PDFTextStripper stripper = new PDFTextStripper();
            text = stripper.getText(document);
            document.close();
        } catch (Exception e) {
            response.setError("Failed to parse PDF file: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }

        if (text == null || text.trim().isEmpty()) {
            response.setError("Could not extract any text from the PDF.");
            return ResponseEntity.badRequest().body(response);
        }

        try {
            // Send extracted text to Python service
            response = nlpService.analyzeResume(text, company, jobDescription);

            // Check if Python service returned an error internally
            if (response != null && response.getError() != null) {
                return ResponseEntity.badRequest().body(response);
            }

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            response.setError("An unexpected error occurred during analysis: " + e.getMessage());
            return ResponseEntity.internalServerError().body(response);
        }
    }

    @GetMapping("/health")
    public String health() {
        return "Backend is running";
    }
}