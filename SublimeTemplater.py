import sublime, sublime_plugin
import re

class Template():
  """
  Some Terminology

  Consider the Underscore/ERB templating system, which has
  tags such as <% %> and <%= %>

  An opener tag is one that is common to all tags in the templating
  system. In this case, it is <%

  Similarly, a closer tag is %>

  Addons are defined as an array of arrays, the latter of which
  have two elements. Given the two tags above, the addons
  are [['', ''], ['=', '']]

  A block is the combination of an opener and its addons, or
  its closer and its addons.

  """


  def __init__(self, opener, closer, addons):
    self.opener = opener
    self.closer = closer
    self.addons = addons
    self.addons_generator = None

  def get_single_multi_re(self, singles, multis, can_be_empty):
    """
    Produces a regular expression that will handle
    single character add-ons, multiple character add-ons,
    and empty character add-ons.
    """
    final_re_list = []

    # If no opener addons, then something like []? is pointless
    if len(singles) > 0:
      single_addon_re = "".join(["\\"+ x for x in singles])
      single_re = "[" + single_addon_re + "]"
      final_re_list.append(single_re)

    if len(multis) > 0:
      multi_re = [re.escape(expr) for expr in multis]
      for mre in multi_re:
        final_re_list.append(mre)

    final_re = "(" + "|".join(final_re_list) + ")"
    if can_be_empty: final_re += "?"

    return final_re

  def get_addon_re(self, position):
    # Gets the nth element in each template addon
    positions = [addon[position] for addon in self.addons]

    # Gets only the unique symbols in that position
    uniques = list(set(positions))

    # Produces a list of non-empty addon symbols at that position
    non_empty = filter((lambda y: y != ""), uniques)

    single_addons = [x for x in non_empty if len(x) == 1]
    multi_addons = [x for x in non_empty if len(x) > 1]
    # If the position is allowed to be empty, make the regexp optional
    can_be_empty = len(non_empty) < len(uniques)

    re = self.get_single_multi_re(single_addons, multi_addons, can_be_empty)

    return re

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
      i = 0
      addon_length = len(self.addons)
      while True:
        if addon_length > 0:
          addons = self.addons[i % addon_length]
        else:
          addons = ['', '']
        argval = yield [self.opener + addons[0], addons[1] + self.closer]
        if argval is None:
          i += 1
        else:
          i = argval

    if self.addons_generator is None:
      self.addons_generator = generator()
      self.addons_generator.send(None)
    return self.addons_generator

class TemplateCollection():
  def __init__(self):
    # ERB, Underscore, EJS
    self.PERCENT_OPENER = "<%"
    self.PERCENT_CLOSER = "%>"
    self.PERCENT_ADDONS = [['', ''], ['=', ''], ['#', ''], ['-', '-'], ['=', '-'], ['', '-']]

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
    self.PHP_QUESTION_ADDONS = [['', ''], ['=', ''], ['#', ''], ['php', '']]

    self.set_percent_template()

  def set_syntax_generator(self, name):
    if name in ["erb", "underscore", "ejs"]:
      self.set_percent_template()
    elif name in ["mustache", "handlebars", "angular"]:
      self.set_braces_template()
    elif name in ["jinja", "twig", "nunjucks"]:
      self.set_brace_percent_template()
    elif name in ["php"]:
      self.set_php_question_template()

  def set_percent_template(self):
    self.template = Template(self.PERCENT_OPENER, self.PERCENT_CLOSER, self.PERCENT_ADDONS)

  def set_braces_template(self):
    self.template = Template(self.BRACES_OPENER, self.BRACES_CLOSER, self.BRACES_ADDONS)

  def set_brace_percent_template(self):
    self.template = Template(self.BRACE_PERCENT_OPENER, self.BRACE_PERCENT_CLOSER, self.BRACE_PERCENT_ADDONS)

  def set_php_question_template(self):
    self.template = Template(self.QUESTION_OPENER, self.QUESTION_CLOSER, self.PHP_QUESTION_ADDONS)

  def get_template(self):
    return self.template

templates = TemplateCollection()

class TemplateListeners(sublime_plugin.EventListener):
  def set_template_syntax(self, view):
    syntax = view.settings().get('syntax').lower()
    file_name = view.file_name()
    if file_name is None:
      file_name = ""
    else:
      file_name = file_name.lower()

    templates.set_percent_template()

    if syntax.find("javascript") >= 0:
      templates.set_percent_template()
    elif syntax.find("angularjs") >= 0:
      templates.set_braces_template()
    elif syntax.find("python") >= 0:
      templates.set_brace_percent_template()
    elif syntax.find("ruby") >= 0 or syntax.find("rails") >= 0:
      templates.set_percent_template()
    elif syntax.find("php") >= 0:
      templates.set_php_question_template()

    if file_name.find("erb", -3) >= 0:
      templates.set_percent_template()

  def set_syntax_change_event_listener(self, view):
    def set_syntax_closure():
      return self.set_template_syntax(view)
    view.settings().add_on_change('syntax', set_syntax_closure)

  def on_load(self, view):
    self.set_template_syntax(view)
    self.set_syntax_change_event_listener(view)

  def on_new(self, view):
    self.set_syntax_change_event_listener(view)

  # Also call set_template_syntax when the syntax is changed
  # What is fired when the syntax changes?

class SyntaxCommand(sublime_plugin.WindowCommand):
  def run(self, syntax):
    templates.set_syntax_generator(syntax)

class TemplaterCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.opener_re = templates.get_template().get_opener_re()
    self.closer_re = templates.get_template().get_closer_re()
    self.generator = templates.get_template().get_addons_generator()

    if len(self.view.sel()) < 1:
      return

    new_selections = []

    for region in self.view.sel():
      opener, closer = self.find_surrounding_blocks(region)

      # Cycle through possible blocks if brackets already exist
      if (opener is not None) and (closer is not None):
        new_selections.append(self.cycle_blocks(edit, opener, closer, region))
      # Insert new blocks if they do not
      else:
        new_selections.append(self.insert_block(edit, region))

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
    found_openers = list(re.finditer(self.opener_re, self.view.substr(left_region)))
    if len(found_openers) > 0:
      # if found, create a region for it using the last match - the rightmost bracket found
      opener = sublime.Region(left_region.begin() + found_openers[-1].start(), left_region.begin() + found_openers[-1].end())

    # Search in the right region for a closing bracket
    found_closers = list(re.finditer(self.closer_re, self.view.substr(right_region)))
    if len(found_closers) > 0:
      # if found, create a region for it using the first match - the leftmost bracket found
      closer = sublime.Region(right_region.begin() + found_closers[0].start(), right_region.begin() + found_closers[0].end())

    return opener, closer

  def insert_block(self, edit, region):
    # insert the first block in the list
    default_block = self.generator.send(0)

    # insert in reverse order because line length might change
    self.view.insert(edit, region.end(), " %s" % default_block[1])
    inserted_before = self.view.insert(edit, region.begin(), "%s " % default_block[0])

    return sublime.Region(region.begin() + inserted_before, region.end() + inserted_before)

  def cycle_blocks(self, edit, opener, closer, region):
    # Get next block to cycle to
    next_block = self.get_next_block(self.view.substr(opener), self.view.substr(closer))

    # Calculate how many characters the selection will change by
    changed_before = len(next_block[0]) - len(self.view.substr(opener))

    # Cycle by replacing in reverse order because line length might change
    self.view.replace(edit, closer, next_block[1])
    self.view.replace(edit, opener, next_block[0])

    return sublime.Region(region.begin() + changed_before, region.end() + changed_before)

  def get_next_block(self, opening_bracket, closing_bracket):
    return next(self.generator)


