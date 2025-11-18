# Test script to verify output_dir parameter works
library(nhlpackageattempt)

# Create directory if it doesn't exist
analytics_dir <- "/Users/emilyfehr8/Desktop/Analytics"
if (!dir.exists(analytics_dir)) {
  dir.create(analytics_dir, recursive = TRUE)
  cat("Created directory:", analytics_dir, "\n")
}

client <- NHLAPIClient$new()
report_gen <- PostGameReportGenerator$new(api_client = client)

cat("\nTesting generate_report with output_dir parameter...\n")
cat("Output directory:", analytics_dir, "\n\n")

# Generate report
report_file <- report_gen$generate_report(
  game_id = 2024020008,
  output_format = "html",
  output_dir = analytics_dir
)

cat("\n✓ Report generated successfully!\n")
cat("Report file:", basename(report_file), "\n")
cat("Location:", dirname(report_file), "\n")
cat("Full path:", report_file, "\n")
