return {
	"danymat/neogen",
	dependencies = "nvim-treesitter/nvim-treesitter",
	opts = {
		languages = {
			python = {
				template = { annotation_convention = "google_docstrings" },
			},
		},
	},
	keys = {
		{ "<leader>cd", "<cmd>Neogen<cr>", desc = "Generate docstring" },
	},
}
