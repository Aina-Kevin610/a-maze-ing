-- Highlight yank
vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function()
    vim.highlight.on_yank({ higroup = "IncSearch", timeout = 150 })
  end,
})

-- Force fond NOIR PUR après chaque colorscheme
vim.api.nvim_create_autocmd("ColorScheme", {
  callback = function()
    local overrides = {
      Normal          = { fg = "#ffffff", bg = "#000000" },
      NormalNC        = { fg = "#ffffff", bg = "#000000" },
      NormalFloat     = { fg = "#ffffff", bg = "#000000" },
      SignColumn      = { bg = "#000000" },
      LineNr          = { fg = "#444444", bg = "#000000" },
      CursorLineNr    = { fg = "#cc00ff", bg = "#000000", bold = true },
      CursorLine      = { bg = "#0a0010" },
      StatusLine      = { bg = "#000000" },
      TabLine         = { bg = "#000000" },
      TabLineFill     = { bg = "#000000" },
      EndOfBuffer     = { bg = "#000000" },
      VertSplit       = { bg = "#000000" },
      -- Bold syntaxe
      ["@keyword"]    = { fg = "#cc00ff", bold = true },
      ["@function"]   = { fg = "#50fa7b", bold = true },
      ["@string"]     = { fg = "#ffdd00", bold = true },
      ["@number"]     = { fg = "#ff9944", bold = true },
      ["@type"]       = { fg = "#00ffcc", bold = true },
      ["@variable"]   = { fg = "#ffffff", bold = true },
      ["@parameter"]  = { fg = "#ff55ff", bold = true },
      Comment         = { fg = "#555555", bold = true, italic = true },
    }
    for group, hl in pairs(overrides) do
      vim.api.nvim_set_hl(0, group, hl)
    end
  end,
})
