package cli

import (
	"fmt"

	"github.com/spf13/cobra"
)

// Version is overridden by build metadata in later release packaging work.
var Version = "0.1.0"

func newVersionCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "version",
		Short: "Print the current version of Rygnal",
		Args:  cobra.NoArgs,
		Run: func(cmd *cobra.Command, _ []string) {
			fmt.Fprintf(cmd.OutOrStdout(), "rygnal version %s\n", Version)
		},
	}
}
