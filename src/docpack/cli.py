# docpack
#     freeze     # turn folders/zips into a .docpack (the freezer)
#     deck       # launch the Flight Deck (TUI / web cockpit)
#     recall     # semantic search against a docpack
#     serve      # expose docpack via MCP for AI agents
#     info       # inspect metadata, stats, counts
#     run        # freeze + serve a temp docpack (one-shot)

# Create a .docpack from a directory or zip:
# docpack freeze ./my-project -o project.docpack

# Open the interactive Flight Deck (TUI or browser):
# docpack deck project.docpack (open right into docpack viewer) || docpack deck (open without loading) || docpack deck --web (open website version)

# Semantic search from the terminal, no TUI:
# docpack recall project.docpack "where is jwt validation handled?"

# Run the MCP server so AI agents can explore the frozen universe:
# docpack serve project.docpack
# This exposes:
# - ls(path)
# - read(path)
# - recall(query)

# Show schema / counts / metadata / stats:
# docpack info project.docpack

# The “just do everything” command — freeze + serve, temp file, auto-cleanup:
# docpack run ./my-project (Equivalent to: freeze → temp.docpack → serve)


def main():
    pass