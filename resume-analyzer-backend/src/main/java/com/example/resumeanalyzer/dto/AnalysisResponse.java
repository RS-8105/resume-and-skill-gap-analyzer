package com.example.resumeanalyzer.dto;

import java.util.List;

public class AnalysisResponse {
    private List<String> present_skills;
    private List<String> missing_skills;
    private double skill_match_percentage;
    private double similarity_score;
    private List<String> recommendations;
    private String error;

    @com.fasterxml.jackson.annotation.JsonProperty("company_overview")
    private String companyOverview;

    @com.fasterxml.jackson.annotation.JsonProperty("company_growth")
    private String companyGrowth;

    @com.fasterxml.jackson.annotation.JsonProperty("role_responsibilities")
    private String roleResponsibilities;

    @com.fasterxml.jackson.annotation.JsonProperty("average_salary")
    private String averageSalary;

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

    public String getCompanyOverview() {
        return companyOverview;
    }

    public void setCompanyOverview(String companyOverview) {
        this.companyOverview = companyOverview;
    }

    public String getCompanyGrowth() {
        return companyGrowth;
    }

    public void setCompanyGrowth(String companyGrowth) {
        this.companyGrowth = companyGrowth;
    }

    public String getRoleResponsibilities() {
        return roleResponsibilities;
    }

    public void setRoleResponsibilities(String roleResponsibilities) {
        this.roleResponsibilities = roleResponsibilities;
    }

    public String getAverageSalary() {
        return averageSalary;
    }

    public void setAverageSalary(String averageSalary) {
        this.averageSalary = averageSalary;
    }

    @com.fasterxml.jackson.annotation.JsonProperty("optimized_resume")
    private String optimizedResume;

    public String getOptimizedResume() {
        return optimizedResume;
    }

    public void setOptimizedResume(String optimizedResume) {
        this.optimizedResume = optimizedResume;
    }

    @com.fasterxml.jackson.annotation.JsonProperty("recommended_companies")
    private List<RecommendedCompany> recommendedCompanies;

    public List<RecommendedCompany> getRecommendedCompanies() {
        return recommendedCompanies;
    }

    public void setRecommendedCompanies(List<RecommendedCompany> recommendedCompanies) {
        this.recommendedCompanies = recommendedCompanies;
    }

    public static class RecommendedCompany {
        private String company;
        private String reason;
        
        @com.fasterxml.jackson.annotation.JsonProperty("fit_score")
        private int fitScore;

        public String getCompany() {
            return company;
        }

        public void setCompany(String company) {
            this.company = company;
        }

        public String getReason() {
            return reason;
        }

        public void setReason(String reason) {
            this.reason = reason;
        }

        public int getFitScore() {
            return fitScore;
        }

        public void setFitScore(int fitScore) {
            this.fitScore = fitScore;
        }
    }
}
