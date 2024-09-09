# CHANGELOG


## 1.0.0 (DEV RELEASE)

- Major API Redesign: The entire API has been restructured for better modularity and flexibility.
- New Type System: Introduced a new type system, replacing the old v1 types.
- Migration Support: Added wrap_legacy_types to help transition from v1 types to the new system without a complete rewrite.
- Enhanced make_executable_schema: Now supports both legacy and new types with improved validation and root type merging.
- Deprecation Notice: Direct use of v1 types is deprecated. Transition to the new system or use wrap_legacy_types for continued support.


## 0.8.0 (2024-02-21)

- Added support for Ariadne 0.22.


## 0.7.0 (2022-09-13)

- Added support for Ariadne schema definitions to `make_executable_schema`.


## 0.6.0 (2022-09-08)

- Added support for `__args__ = convert_case` for `MutationType`.
- Changed `convert_case` to be less magic in its behavior.


## 0.5.0 (2022-07-03)

- Implement missing logic for `ObjectType.__fields_args__`


## 0.4.0 (2022-05-04)

- Split logic from `BaseType` into `DefinitionType` and `BindableType`.
- Add `CollectionType` utility type for gathering types into single type.


## 0.3.0 (2022-04-25)

- Fix "dependency required" error raised for GraphQL `Float` scalar type.
