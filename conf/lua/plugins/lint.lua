return {
	-- Gestionnaire d'outils (mypy, flake8, black...)
	{
		"williamboman/mason.nvim",
		opts = {},
	},

	-- Installe automatiquement les linters via mason
	{
		"jay-babu/mason-null-ls.nvim",
		event = { "BufReadPre", "BufNewFile" },
		dependencies = {
			"williamboman/mason.nvim",
			"nvimtools/none-ls.nvim",
		},
		opts = {
			ensure_installed = { "mypy", "flake8" },
			automatic_installation = true,
		},
	},

	-- Branche mypy/flake8 dans le système LSP
	{
		"nvimtools/none-ls.nvim",
		dependencies = { "nvim-lua/plenary.nvim" },
		config = function()
			local null_ls = require("null-ls")
			null_ls.setup({
				sources = {
					null_ls.builtins.diagnostics.mypy.with({
						extra_args = { "--ignore-missing-imports" },
					}),
					null_ls.builtins.diagnostics.flake8.with({
						extra_args = { "--max-line-length=88" }, -- compatible black
					}),
				},
			})
		end,
	},

	-- Panneau d'erreurs propre
	{
		"folke/trouble.nvim",
		opts = {},
		keys = {
			{ "<leader>xx", "<cmd>Trouble diagnostics toggle<cr>", desc = "Diagnostics" },
		},
	},
}
