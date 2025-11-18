# Generate WPG (Winnipeg Jets) Report
# Run this script in R or RStudio

library(nhlpackageattempt)

cat("=== Generating WPG Report ===\n\n")

# Create API client
client <- NHLAPIClient$new()

# Create report generator
report_gen <- PostGameReportGenerator$new(api_client = client)

# WPG game ID: 2024020008 (WPG vs EDM)
game_id <- 2024020008

cat("Game ID:", game_id, "\n")
cat("Game: WPG vs EDM\n")
cat("Generating report...\n\n")

# Generate the report (will automatically use HTML since LaTeX is not available)
report_file <- report_gen$generate_report(
  game_id = game_id,
  output_format = "html"
)

cat("\n✓ Report generated successfully!\n")
cat("Report file:", report_file, "\n")
cat("Location:", getwd(), "\n")
cat("\nYou can open this HTML file in your web browser.\n")

# Optionally open the file automatically (uncomment if desired)
# browseURL(report_file)
