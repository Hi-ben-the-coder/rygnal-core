package cli

import "github.com/spf13/cobra"

const (
	productName = "rygnal"
	shortDesc   = "Rygnal is an AI Agent Guardrails platform"
	longDesc    = "An enterprise-grade runtime containment and safety gate layer for autonomous AI agents."
)

// Execute runs the production CLI entrypoint.
func Execute() error {
	return NewRootCommand().Execute()
}

// NewRootCommand constructs the root command.
//
// It is intentionally exported for tests so command behavior can be verified
// without mutating global Cobra state.
func NewRootCommand() *cobra.Command {
	rootCmd := &cobra.Command{
		Use:           productName,
		Short:         shortDesc,
		Long:          longDesc,
		SilenceUsage:  true,
		SilenceErrors: true,
	}

	rootCmd.CompletionOptions.DisableDefaultCmd = true

	rootCmd.AddCommand(newVersionCmd())
	rootCmd.AddCommand(newRunCmd())

	return rootCmd
}
