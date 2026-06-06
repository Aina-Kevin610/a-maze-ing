return {
	{
		"akinsho/toggleterm.nvim",
		version = "*",
		keys = { "<C-t>" },
		opts = {
			open_mapping = [[<C-t>]],
			direction = "float",
			float_opts = {
				border = "curved",
				winblend = 10,
			},
			highlights = {
				FloatBorder = { fg = "#cc00ff" },
			},
		},
	},
}
