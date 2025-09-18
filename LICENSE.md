# License

This project is licensed under the terms of the [MIT] License.

## Preferred Code Copyright Text

Line comments are to be preferred over block comments when including license text.
Include your E-mail is preferred but optional.
If you choose to not include your e-mail please ensure the project has some
means to contact you should there be questions about the submitted code.
You can send the contact information confidentially via an e-mail to:
[Michael Cummings](mailto:mgcummings@yahoo.com?subject=Contact%20Info%3A%20option)

Replace text within `[]` with your own information in the following templates:

```
# Copyright © [YEAR] [Your Name] <[(Your E-mail]>
#
# Licensed under the MIT license
# [MIT](https:#opensource.org/license/mit-0).
#
# Files in this project may not be copied, modified, or distributed except
# according to those terms.
#
# The full text of the license can be found in the project LICENSE.md file.
#
# SPDX-License-Identifier: MIT
##############################################################################
```

If you are using a [JetBrains] based IDE you can add to
`Settings > Editor > Copyright > Copyright Profiles`
the following copyright profile:

```velocity
Copyright © $originalComment.match("Copyright © (\d+)", 1, "-", "$today.year")$today.year [Your Name] <[(Your E-mail]>

Licensed under the MIT license
[MIT](https://opensource.org/license/mit-0).

Files in this project may not be copied, modified, or distributed except
according to those terms.

The full text of the license can be found in the project LICENSE.md file.

SPDX-License-Identifier: MIT
```

The following options in `Settings > Editor > Copyright > Formating` will match
current copyright styling used in the project:

* Comment Type:
    - (*) Use line comment
* Relative Location:
    - (*) Before other comments
* Borders:
    - (*) Seperator After
    - Length: ___80___
    - (*) Blank Line After

Finally make sure you select the correct profile in
`Settings > Editor > Copyright` for:

* Default project copyright: ___Your Profile Name___

## MIT License

This project includes code licensed under the MIT License.
The full text of the MIT License is provided below.

    The MIT License (MIT)
    =====================

    Copyright © 2025 Michael Cummings <mgcummings@yahoo.com>

    Permission is hereby granted, free of charge, to any person
    obtaining a copy of this software and associated documentation
    files (the “Software”), to deal in the Software without
    restriction, including without limitation the rights to use,
    copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be
    included in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
    OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
    NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
    WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.


[JetBrains]: https://www.jetbrains.com/

[MIT]: https://opensource.org/licenses/MIT
