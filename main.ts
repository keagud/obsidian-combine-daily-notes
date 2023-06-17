import { Plugin, App, Notice, FileSystemAdapter } from "obsidian";
import { execFile } from "child_process";
import * as path from "path";

function getVaultRoot(app: App): string {
  let adapter = app.vault.adapter;

  if (adapter instanceof FileSystemAdapter) {
    return adapter.getBasePath();
  }
  throw "Can't find the vault root path";
}

module.exports = class CombineDailyNotes extends Plugin {
  async onload() {
    const vault_root = getVaultRoot(this.app);

    const config_dir = this.app.vault.configDir

    // this is a bad hack
    // but it works for now
    const py_script = path.join(vault_root, config_dir, "plugins", "obsidian-combine-daily-notes", "combine.py")
    
    const output_dir = path.join(vault_root, "Weekly/");

    return execFile(
      py_script,

      [vault_root, output_dir, "clean"],
      
      (error, stdout, stderr) => {
        if (error) {
          
          new Notice(stderr)
          throw error;
          
        }
      }
    );
  }

  async onunload(): Promise<void> {}
};
