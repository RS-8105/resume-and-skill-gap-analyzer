package com.example.resumeanalyzer.dto;

import java.util.List;

public class AnalysisResponse {
    private List<String> present_skills;
    private List<String> missing_skills;
    private double skill_match_percentage;
    private double similarity_score;
    private List<String> recommendations;
    private String error;

    public AnalysisResponse() {
    }

    public List<String> getPresent_skills() {
        return present_skills;
    }

    public void setPresent_skills(List<String> present_skills) {
        this.present_skills = present_skills;
    }

    public List<String> getMissing_skills() {
        return missing_skills;
    }

    public void setMissing_skills(List<String> missing_skills) {
        this.missing_skills = missing_skills;
    }

    public double getSkill_match_percentage() {
        return skill_match_percentage;
    }

    public void setSkill_match_percentage(double skill_match_percentage) {
        this.skill_match_percentage = skill_match_percentage;
    }

    public double getSimilarity_score() {
        return similarity_score;
    }

    public void setSimilarity_score(double similarity_score) {
        this.similarity_score = similarity_score;
    }

    public List<String> getRecommendations() {
        return recommendations;
    }

    public void setRecommendations(List<String> recommendations) {
        this.recommendations = recommendations;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }
}
