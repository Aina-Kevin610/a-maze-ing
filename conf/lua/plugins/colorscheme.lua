return {
  { "LazyVim/LazyVim", opts = { colorscheme = "catppuccin" } },
  {
    "catppuccin/nvim",
    name = "catppuccin",
    priority = 1000,
    opts = {
      flavour = "mocha",
      transparent_background = false, -- fond noir pur
      color_overrides = {
        mocha = {
          -- Fond très sombre comme VSCode
          base     = "#050505",
          mantle   = "#030303",
          crust    = "#000000",
          surface0 = "#0d0d0d",
          surface1 = "#141414",
          surface2 = "#1e1e1e",
          overlay0 = "#444444",
          overlay1 = "#666666",
          overlay2 = "#888888",
          -- Syntaxe vibrante
          text     = "#ffffff",
          mauve    = "#cc00ff",   -- violet/magenta
          pink     = "#ff55ff",
          red      = "#ff5555",
          peach    = "#ff9944",   -- orange
          yellow   = "#ffdd00",   -- jaune vif
          green    = "#50fa7b",   -- vert vif
          teal     = "#00ffcc",   -- cyan
          sky      = "#00bfff",   -- bleu clair
          sapphire = "#4499ff",
          blue     = "#4488ff",
          lavender = "#aa88ff",
        },
      },
      -- Bold partout
      styles = {
        comments    = { "bold", "italic" },
        conditionals = { "bold" },
        loops       = { "bold" },
        functions   = { "bold" },
        keywords    = { "bold" },
        strings     = { "bold" },
        variables   = { "bold" },
        numbers     = { "bold" },
        booleans    = { "bold" },
        properties  = { "bold" },
        types       = { "bold" },
        operators   = { "bold" },
      },
      highlight_overrides = {
        mocha = function(c)
          return {
            -- Fond noir pur
            Normal         = { fg = c.text,   bg = "#050505" },
            NormalNC       = { fg = c.text,   bg = "#030303" },
            NormalFloat    = { fg = c.text,   bg = "#0d0d0d" },
            -- Curseur magenta comme kitty
            Cursor         = { fg = "#000000", bg = "#cc00ff" },
            CursorLine     = { bg = "#0d0d1a" },
            CursorLineNr   = { fg = "#cc00ff", bold = true },
            -- Ligne de status
            StatusLine     = { fg = c.text,   bg = "#0d0d0d" },
            -- Recherche
            Search         = { fg = "#000000", bg = "#ffdd00" },
            IncSearch      = { fg = "#000000", bg = "#cc00ff" },
            -- Sélection
            Visual         = { bg = "#1a0030" },
            -- Numéros de ligne
            LineNr         = { fg = "#444444" },
            -- Indentation
            IndentBlanklineChar = { fg = "#1a1a1a" },
          }
        end,
      },
      integrations = {
        blink_cmp   = true,
        bufferline  = true,
        gitsigns    = true,
        noice       = true,
        treesitter  = true,
        which_key   = true,
        lsp_trouble = true,
        flash       = true,
        mini        = { enabled = true },
        snacks      = { enabled = true },
      },
    },
  },
}
