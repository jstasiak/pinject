"""Copyright 2013 Google Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import types

import binding_keys
import decorators
import errors


class ObjectProvider(object):

    def __init__(self, binding_mapping, bindable_scopes, allow_injecting_none):
        self._binding_mapping = binding_mapping
        self._bindable_scopes = bindable_scopes
        self._allow_injecting_none = allow_injecting_none

    def provide_from_binding_key(self, binding_key, injection_context):
        binding = self._binding_mapping.get(binding_key)
        scope = self._bindable_scopes.get_sub_scope(binding)
        provided = scope.provide(
            binding_key,
            lambda: binding.proviser_fn(injection_context.get_child(binding), self))
        if (provided is None) and not self._allow_injecting_none:
            raise errors.InjectingNoneDisallowedError()
        return provided

    def provide_class(self, cls, injection_context):
        if type(cls.__init__) is types.MethodType:
            init_kwargs = self.get_injection_kwargs(
                cls.__init__, injection_context)
        else:
            init_kwargs = {}
        return cls(**init_kwargs)

    def call_with_injection(self, provider_fn, injection_context):
        kwargs = self.get_injection_kwargs(provider_fn, injection_context)
        return provider_fn(**kwargs)

    def get_injection_kwargs(self, fn, injection_context):
        return binding_keys.create_kwargs(
            decorators.get_injectable_arg_binding_keys(fn),
            lambda bk: self.provide_from_binding_key(bk, injection_context))