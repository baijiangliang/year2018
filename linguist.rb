require 'rugged'
require 'linguist'
require 'json'

# Puts a JSON of language names and corresponding file names.
def detect_code_files()
  if ARGV.length != 1 then
    puts 'Usage: ruby linguist.rb repo_path'
  end
  repo_path = ARGV[0]
  repo = Rugged::Repository.new(repo_path)
  project = Linguist::Repository.new(repo, repo.head.target_id)
  puts JSON.generate(project.breakdown_by_file)
end

detect_code_files()