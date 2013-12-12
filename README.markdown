SublimeTemplater
===
**A fork of SublimeERB, generalized to multiple templating systems**

## Getting Started
SublimeTemplater helps you insert template tags - Underscore's `<% %>`, PHP's `<? ?>`, or Angular's `{{ }}`, and more - into your documents with one shortcut key. Inspired and forked from SublimeERB, repeated keypresses also allows you to cycle through a list of different template tags (`<% %>` to `<%= %>`). Template tags will also automatically surround selected text.

# Installation
## Package Control Installation
When SublimeTemplater is officially released it will be available on [Sublime Package Control](https://sublime.wbond.net/). Press `ctrl`+`shift`+`p` on Windows/Linux and `cmd`+`shift`+`p` on a Mac to bring up Sublime's Command Pallete, then type `install package` to bring up Package Control's package selector. It should be the first selection. Type "SublimeERB," which, again, should be the first selection, and then hit enter.

### Quick Manual Installation: Mac OS X
Run the following commands:
`git clone https://github.com/garetht/SublimeTemplater.git ~/.sublime_templater`
`ln -fs ~/.sublime_templater/ ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/SublimeTemplater`

### Quick Manual Installation: Linux
Run the following commands:
`git clone https://github.com/garetht/SublimeTemplater.git ~/.sublime_templater`
`ln -fs ~/.sublime_templater/ ~/.config/sublime-text-2/Packages/SublimeTemplater`

### Quick Manual Installation: Windows
Instructions are unavailable at this time.


### Manual Installation: Mac OS X and Linux
1. Clone the repository with `git clone https://github.com/garetht/SublimeTemplater.git`
2. Move the repository to the Packages directory of Sublime Text, or make a symbolic link to it.

By default, the shortcut to toggle templates is bound to `ctrl`+`shift`+`p`, but you can change this in your user settings.

### Sublime Text 3 Support

Sublime Text 3 support is not available at this time.


# Usage

### Add Keybinding

Open your User Keybinding File and add the following keybinding to activate the toggle command in all file types:

```json
  [
    { "keys": ["ctrl+shift+."], "command": "templater" }
  ]
```

...or only in the most common ERB contexts:

```json
  [
    { "keys": ["ctrl+shift+."], "command": "erb", "context":
      [
        { "key": "selector", "operator": "equal", "operand": "text.html.ruby, text.haml, source.yaml, source.css, source.scss, source.js, source.coffee" }
      ]
    }
  ]
```

Now you can use `ctrl+shift+.` to create and toggle between ERB tags. NOTE: On a Mac use the command key for the ctrl key.

## Update To Latest Version

If you followed the quick manual install instructions, you can use these commands to update your installation of SublimeTemplater.

```
  cd ~/.sublime_templater
  git pull --rebase
```

#### Copyright
**SublimeTemplater** is copyrighted 2013 by [Gareth Tan](http://garethtan.com), and is released under the MIT License.

**SublimeERB** is Copyright (c) 2011 [Carlos Rodriguez](http://eddorre.com), released under the MIT License.
