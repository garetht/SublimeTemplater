import sublime, sublime_plugin
import re

class TemplateGenerator():
  def __init__(self, opener, closer, addons):
    self.opener = opener
    self.closer = closer
    self.addons = addons

  def get_addon_re(self, position):
    # Gets the nth element in each template addon
    positions = [addon[position] for addon in self.addons]

    # Gets only the unique symbols in that position
    uniques = list(set(positions))

    # Produces a list of non-empty addon symbols at that position
    non_empty = filter((lambda y: y != ""), uniques)

    # If the position is allowed to be empty, make the regexp optional
    opt = "?" if len(non_empty) < len(uniques) else ""
    opener_addons = "".join(["\\"+ x for x in non_empty])

    return "[" + opener_addons + "]" + opt

  def get_opener_re(self):
    opener = re.escape(self.opener)
    closer = re.escape(self.closer)

    addon_re = self.get_addon_re(0)
    return opener + addon_re + "(?!.*" + closer + ")"

  def get_closer_re(self):
    # to check for opener, find position of regexp match
    # and check if there is an opener in that region.

    #for now, ignore that
    closer = re.escape(self.closer)

    addon_re = self.get_addon_re(1)
    return addon_re + closer

  def get_addons_generator(self):
    def generator():
      self.

class TemplateCollection():
  def __init__(self):
    # ERB, Underscore, EJS
    self.PERCENT_OPENER = "<%"
    self.PERCENT_CLOSER = "%>"
    self.PERCENT_ADDONS = [['=', ''], ['', ''], ['-', '-'], ['=', '-'], ['#', ''], ['', '-']]

    # Mustache, Handlebars
    self.BRACES_OPENER = "{{"
    self.BRACES_CLOSER = "}}"
    self.BRACES_ADDONS = []

    # Jinja, Twig, Nunjucks
    self.BRACE_PERCENT_OPENER = "{"
    self.BRACE_PERCENT_CLOSER = "}"
    self.BRACE_PERCENT_ADDONS = [['%', '%'], ['{', '}']]

    # PHP
    self.QUESTION_OPENER = "<?"
    self.QUESTION_CLOSER = "?>"
    self.QUESTION_ADDONS = [['=', ''], ['#', ''], ['php', '']]

  def set_syntax_generator(self, name):
    generator = None
    if name in ["erb", "underscore", "ejs"]:
      generator = self.get_percent_generator()
    elif name in ["mustache", "handlebars"]:
      generator = self.get_braces_generator()
    elif name in ["jinja", "twig", "nunjucks"]:
      generator = self.get_brace_percent_generator()
    elif name in ["php"]:
      generator = self.get_question_generator()

    return generator

  def set_percent_generator():
    pass

  def set_braces_generator(self):
    pass

  def set_brace_percent_generator(self):
    pass

  def set_question_generator(self):
    pass

class SyntaxCommand(sublime_plugin.WindowCommand):
    def __init__():
      pass

    def run(self, syntax):
      pass

class TemplateCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    if len(self.view.sel()) < 1:
      return

    new_selections = []

    for region in self.view.sel():
      opener, closer = self.find_surrounding_blocks(region)

      # Cycle through possible blocks if brackets already exist
      if (opener is not None) and (closer is not None):
        new_selections.append(self.cycle_erb_block(edit, opener, closer, region))
      # Insert new blocks if they do not
      else:
        new_selections.append(self.insert_erb_block(edit, region))

    self.view.sel().clear()

    for selection in new_selections:
      self.view.sel().add(selection)

  def find_surrounding_blocks(self, region):
    opener = None
    closer = None

    # Grab the whole line
    containing_line = self.view.line(region)

    # Create one region on the left of the selection,
    # and another on the right
    left_region = sublime.Region(containing_line.begin(), region.begin())
    right_region = sublime.Region(containing_line.end(), region.end())

    # Search in the left region for an opening bracket
    found_openers = list(re.finditer(ERB_OPENER_REGEX, self.view.substr(left_region)))
    if len(found_openers) > 0:
      # if found, create a region for it using the last match - the rightmost bracket found
      opener = sublime.Region(left_region.begin() + found_openers[-1].start(), left_region.begin() + found_openers[-1].end())

    # Search in the right region for a closing bracket
    found_closers = list(re.finditer(ERB_CLOSER_REGEX, self.view.substr(right_region)))
    if len(found_closers) > 0:
      # if found, create a region for it using the first match - the leftmost bracket found
      closer = sublime.Region(right_region.begin() + found_closers[0].start(), right_region.begin() + found_closers[0].end())

    return opener, closer

  def insert_erb_block(self, edit, region):
    # insert the first block in the list
    default_block = ERB_BLOCKS[0]

    # insert in reverse order because line length might change
    self.view.insert(edit, region.end(), " %s" % default_block[1])
    inserted_before = self.view.insert(edit, region.begin(), "%s " % default_block[0])

    return sublime.Region(region.begin() + inserted_before, region.end() + inserted_before)

  def cycle_erb_block(self, edit, opener, closer, region):
    # Get next block to cycle to
    next_block = self.get_next_erb_block(self.view.substr(opener), self.view.substr(closer))

    # Calculate how many characters the selection will change by
    changed_before = len(next_block[0]) - len(self.view.substr(opener))

    # Cycle by replacing in reverse order because line length might change
    self.view.replace(edit, opener, next_block[1])
    self.view.replace(edit, opener, next_block[0])

    return sublime.Region(region.begin() + changed_before, region.end() + changed_before)

  def get_next_erb_block(self, opening_bracket, closing_bracket):
    for i, block in enumerate(ERB_BLOCKS):
      if [opening_bracket, closing_bracket] == block:
        if i + 1 >= len(ERB_BLOCKS):
          return ERB_BLOCKS[0]
        else:
          return ERB_BLOCKS[i + 1]
    return ERB_BLOCKS[0]


