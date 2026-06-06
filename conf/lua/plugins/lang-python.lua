return {
	{
		"neovim/nvim-lspconfig",
		opts = {
			servers = {
				pyright = {}, -- types + inlay hints
				ruff_lsp = {}, -- linting (flake8 + plus)
			},
		},
	},
}
